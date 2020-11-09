from os import path
from statistics import mean
from typing import Iterable
from utils.date_utils import windows_path_friendly_now

from configs import RESULTS_DIR_PATH
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.inspection import permutation_importance
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)
from sklearn.pipeline import make_pipeline
from utils.classifier_utils import store_collection, store_joblib, store_json, store_onnx


class TrainedRefactoringMLModel:
    def __init__(self, model_name: str, dataset_name: str, target_refactoring: str, model: BaseEstimator, scaler: TransformerMixin, feature_names: Iterable[str]) -> None:
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.target_refactoring = target_refactoring
        self.model = model
        self.scaler = scaler
        self.feature_names = feature_names
        self.created_at_path_friendly = windows_path_friendly_now()

    def persist_model(self):
        """
        Persist this model with reference to its dataset, refactoring_type, features, model
        and if specified also the prediction results for the validation sets.
        """
        results_dir = self._results_dir()
        model = self.model
        scaler = self.scaler
        feature_names = self.feature_names

        pipeline = make_pipeline(scaler, model)

        for model, filename in zip([pipeline, model, scaler], ['pipeline.joblib', 'model.joblib', 'scaler.joblib']):
            store_joblib(model, path.join(results_dir, filename))

        store_collection(feature_names, path.join(
            results_dir, 'feature_names'))
        store_onnx(path.join(results_dir, 'pipeline.onnx'),
                   pipeline, feature_names)

    def persist_validation_statistics(self, val_sets_names, val_sets_x_list, val_sets_y_list):
        results_dir = self._results_dir()
        validation_statistics_path = path.join(
            results_dir, "validation_statistics.json")
        store_json(self.get_validation_results(
            val_sets_names, val_sets_x_list, val_sets_y_list), validation_statistics_path)

    def persist_model_parameters(self):
        results_dir = self._results_dir()

        model_parameters_path = path.join(
            results_dir, "model_parameters.json")
        store_json(self._model_parameters(), model_parameters_path)

    def persist_validation_prediction_results(self, db_ids, val_names, x_val_list, y_val_list):
        results_dir = self._results_dir()
        validation_prediction_results_path = path.join(
            results_dir, "validation_prediction_results.json")
        res = {val_name: self._val_results(db_id, y_val, x) for val_name, db_id, x, y_val in zip(
            val_names, db_ids, x_val_list, y_val_list)}
        store_json(res, validation_prediction_results_path)

    def _results_dir(self) -> str:
        return path.join(RESULTS_DIR_PATH, self.dataset_name, self.target_refactoring, self.model_name, self.created_at_path_friendly)

    def _val_results(self, db_ids, y_val, x):
        y_pred = self.model.predict(x).tolist()
        return {db_id: {"real_y": real_y, "predicted_y": predicted_y} for db_id, real_y, predicted_y in zip(db_ids, y_val, y_pred)}

    def _model_parameters(self):
        model = self.model
        metadata = {"model_parameters": self.model.get_params()}

        # some models have the 'coef_' attribute, and others have the 'feature_importances_
        # coefficients is also nested in a list so we get the first element.
        if hasattr(model, "coef_"):
            best_model_coefficients = model.coef_[0]
            metadata["coefficients"] = {feature: coef for feature,
                                        coef in zip(self.feature_names, best_model_coefficients)}
        elif hasattr(model, "feature_importances_"):
            metadata["feature_importances"] = {feature: importance for feature, importance in zip(
                self.feature_names, model.feature_importances_)}
        return metadata

    def calculate_validation_metrics(self, x_val, y_val):
        training_model = self.model
        y_pred = training_model.predict(x_val)
        numpy_permutation_importance = permutation_importance(
            training_model, x_val, y_val, n_repeats=30, random_state=237)

        conf_matrix = confusion_matrix(y_val, y_pred).ravel().tolist()

        feat = {feature: {"mean": mean, "std": std} for feature, mean, std in zip(
                self.feature_names, numpy_permutation_importance.importances_mean, numpy_permutation_importance.importances_std)}

        val_scores = {"accuracy_score": accuracy_score(y_val, y_pred),
                      "f1_score": f1_score(y_val, y_pred),
                      "precision": precision_score(y_val, y_pred),
                      "confusion_matrix": {'tn': conf_matrix[0], 'fp': conf_matrix[1], 'fn': conf_matrix[2],  'tp': conf_matrix[3]},
                      "recall_score": recall_score(y_val, y_pred),
                      "permutation_importance": feat}
        return val_scores

    def _calculate_mean(self, val_names_results: dict, to_calculate_mean_of):
        return mean([results[to_calculate_mean_of] for results in val_names_results.values()])

    def get_validation_results(self, val_sets_names, val_sets_x_list, val_sets_y_list):
        """
        Format all specified scores and other relevant data of the validation in a json format.
        """
        val_names_results = {name: self.calculate_validation_metrics(x, y) for name,
                             x, y in zip(val_sets_names, val_sets_x_list, val_sets_y_list)}

        means = {}
        for to_calculate_mean_of in ['f1_score', 'precision', 'recall_score', 'accuracy_score']:
            means[f'mean_{to_calculate_mean_of}'] = self._calculate_mean(
                val_names_results, to_calculate_mean_of)
        val_names_results.update(means)

        return val_names_results
