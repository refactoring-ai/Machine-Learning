from os import path
from statistics import mean
from typing import Iterable
from utils.log import log

from configs import (
    BALANCE_DATASET,
    BALANCE_DATASET_STRATEGY,
    PERM_PAR,
    PERM_REPEATS,
    RESULTS_DIR_PATH,
    SEED)
from pandas import Series
from pandas.core.frame import DataFrame
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.inspection import permutation_importance
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)
from sklearn.pipeline import make_pipeline
from utils.classifier_utils import \
    store_collection, store_joblib, store_json, store_onnx


class TrainedRefactoringMLModel:
    def __init__(
            self,
            model_name: str,
            dataset_name: str,
            target_refactoring: str,
            model: BaseEstimator,
            scaler: TransformerMixin,
            feature_names: Iterable[str],
            time_path_friendly: str,
            commit_threshold: int,
            production_model: bool,
            feature_reduction: bool) -> None:
        self._model_name = model_name
        self._dataset_name = dataset_name
        self._target_refactoring = target_refactoring
        self._model = model
        self._scaler = scaler
        self._feature_names = feature_names
        self._created_at_path_friendly = time_path_friendly
        self._commit_threshold = commit_threshold
        self.model_parameters = None
        self.validation_statistics = None
        self.validation_prediction_results = None
        self._is_production_model = production_model
        self.feature_reduction = feature_reduction

    def persist_model(self):
        """
        Persist this model with reference to its dataset,
        refactoring_type, features, model
        and if specified also the prediction results for the validation sets.
        """
        results_dir = self._results_dir()
        model = self._model
        scaler = self._scaler
        feature_names = self._feature_names
        store_collection(feature_names, path.join(
            results_dir, 'feature_names'))

        if scaler is not None:
            pipeline = make_pipeline(scaler, model)
            for model, filename in zip([pipeline, model, scaler],
                                       [
                                       'pipeline.joblib',
                                       'model.joblib',
                                       'scaler.joblib'
                                       ]):
                store_joblib(model, path.join(results_dir, filename))
            store_onnx(
                path.join(
                    results_dir,
                    'pipeline.onnx'),
                pipeline,
                self._model_name,
                feature_names,
                self._target_refactoring,
                self._dataset_name)
        else:
            store_joblib(model, path.join(results_dir, 'model.joblib'))
            store_onnx(
                path.join(
                    results_dir,
                    'model.onnx'),
                model,
                self._model_name,
                feature_names,
                self._target_refactoring,
                self._dataset_name)

    def persist_validation_statistics(
            self,
            val_sets_names,
            val_sets_x_list,
            val_sets_y_list):
        results_dir = self._results_dir()
        validation_statistics_path = path.join(
            results_dir, "validation_statistics.json")
        self.validation_statistics = self.get_validation_results(
            val_sets_names, val_sets_x_list, val_sets_y_list)
        store_json(self.validation_statistics, validation_statistics_path)

    def persist_data(
            self,
            X: DataFrame,
            y: DataFrame,
            X_train: DataFrame,
            y_train: DataFrame,
            X_val: DataFrame,
            y_val: DataFrame):
        results_dir = self._results_dir()

        def save_to_ftr(df: DataFrame, name: str):
            if isinstance(df, Series):
                df = df.to_frame()
            df_with_column_index = df.reset_index()
            df_with_column_index.to_feather(
                path.join(results_dir, f"{name}.ftr"))
        for df, name in zip([X, y, X_train, y_train, X_val, y_val], [
                            "X", "y", "X_train", "y_train", "X_val", "y_val"]):
            save_to_ftr(df, name)

    def persist_model_parameters(self):
        results_dir = self._results_dir()

        model_parameters_path = path.join(
            results_dir, "model_parameters.json")
        self.model_parameters = self._model_parameters()
        store_json(self.model_parameters, model_parameters_path)

    def persist_validation_prediction_results(
            self, db_ids, val_names, x_val_list, y_val_list):
        results_dir = self._results_dir()
        validation_prediction_results_path = path.join(
            results_dir, "validation_prediction_results.json")
        self.validation_prediction_results = {
            val_name: self._val_results(
                db_id, y_val, x) for val_name, db_id, x, y_val in zip(
                val_names, db_ids, x_val_list, y_val_list)}
        store_json(self.validation_prediction_results,
                   validation_prediction_results_path)

    def _results_dir(self) -> str:
        model_type = "production" if self._is_production_model else "training"
        return path.join(RESULTS_DIR_PATH,
                         "models",
                         model_type,
                         str(self._commit_threshold),
                         self._model_name,
                         self._target_refactoring,
                         "balanced" if BALANCE_DATASET else "non-balanced",
                         self._dataset_name,
                         self._created_at_path_friendly).replace(' ', '-')

    def _val_results(self, db_ids, y_val, x):
        y_pred = self.model.predict(x).tolist()
        return {db_id: {"real_y": real_y, "predicted_y": predicted_y}
                for db_id, real_y, predicted_y in zip(db_ids, y_val, y_pred)}

    def _model_parameters(self):
        model = self._model

        metadata = {"model_parameters": self._model.get_params()}
        if BALANCE_DATASET:
            metadata["balanced"] = True
            metadata["balanced_strategy"] = BALANCE_DATASET_STRATEGY
        else:
            metadata["balanced"] = False

        # coefficients is nested in a list so we get the first element.
        if hasattr(model, "coef_"):
            coefficients = {feature: coef for feature,
                            coef in zip(self._feature_names, model.coef_[0])}
            coefficients_sorted = {k: v for k, v in sorted(
                coefficients.items(), key=lambda item: item[1])}
            metadata["coefficients"] = coefficients_sorted
        elif hasattr(model, "feature_importances_"):
            feature_importances = {
                feature: importance for feature,
                importance in zip(
                    self._feature_names,
                    model.feature_importances_)}
            feature_importances_sorted = {k: v for k, v in sorted(
                feature_importances.items(), key=lambda item: item[1])}
            metadata["feature_importances"] = feature_importances_sorted

        return metadata

    def calculate_validation_metrics(self, x_val, y_val):
        training_model = self._model
        log("predicting on val set")
        y_pred = training_model.predict(x_val)
        log("calculating perm importance")
        numpy_permutation_importance = permutation_importance(
            training_model,
            x_val,
            y_val,
            n_repeats=PERM_REPEATS,
            random_state=SEED,
            n_jobs=PERM_PAR)

        log("calculating confusion matrix")
        conf_matrix = confusion_matrix(y_val, y_pred).ravel().tolist()

        feature_importances = {
            feature: {
                "importance": importance.tolist(),
                "mean": mean,
                "std": std} for feature,
            importance,
            mean,
            std in zip(
                self._feature_names,
                numpy_permutation_importance.importances,
                numpy_permutation_importance.importances_mean,
                numpy_permutation_importance.importances_std)}
        val_scores = {
            "accuracy_score": accuracy_score(
                y_val,
                y_pred),
            "f1_score": f1_score(
                y_val,
                y_pred),
            "precision": precision_score(
                y_val,
                y_pred),
            "confusion_matrix": {
                'true_negative': conf_matrix[0],
                'false_positive': conf_matrix[1],
                'false_negative': conf_matrix[2],
                'true_positive': conf_matrix[3]},
            "recall_score": recall_score(
                y_val,
                y_pred),
            "permutation_importance_summary": feature_importances,
            "permutation_importance": feature_importances}
        if hasattr(self._model, "oob_score_"):
            val_scores["oob_score"] = self._model.oob_score_

        return val_scores

    def _calculate_mean(self, val_names_results: dict, to_calculate_mean_of):
        return mean([results[to_calculate_mean_of]
                     for results in val_names_results.values()])

    def get_validation_results(
            self,
            val_sets_names,
            val_sets_x_list,
            val_sets_y_list):
        """
        Format all specified scores
        and other relevant data of the validation in a json format.
        """
        val_names_results = {
            name: self.calculate_validation_metrics(
                x, y) for name, x, y in zip(
                val_sets_names, val_sets_x_list, val_sets_y_list)}

        means = {}
        for to_calculate_mean_of in [
            'f1_score',
            'precision',
            'recall_score',
                'accuracy_score']:
            means[f'mean_{to_calculate_mean_of}'] = self._calculate_mean(
                val_names_results, to_calculate_mean_of)
        val_names_results.update(means)

        return val_names_results
