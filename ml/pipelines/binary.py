import traceback
from typing import Dict, Iterable

import pandas as pd
from configs import (CORE_COUNT, N_CV_SEARCH, N_ITER_RANDOM_SEARCH, SCORING,
                     SEARCH, VAL_SPLIT_SIZE, VALIDATION_DATASETS)
from ml.models.base import SupervisedMLRefactoringModel
from ml.models.trained_refactoring_model import TrainedRefactoringMLModel
from ml.pipelines.pipelines import MLPipeline
from ml.preprocessing.feature_reduction import perform_feature_reduction
from ml.preprocessing.preprocessing import retrieve_labelled_instances
from ml.refactoring import LowLevelRefactoring
from pandas.core.frame import DataFrame
from sklearn.base import TransformerMixin
from sklearn.model_selection import (GridSearchCV, RandomizedSearchCV,
                                     StratifiedKFold, train_test_split)
from utils.classifier_utils import format_best_parameters
from utils.date_utils import now
from utils.log import log


class BinaryClassificationPipeline(MLPipeline):
    """
    Train models for binary classification
    """

    def __init__(self, models_to_run: Iterable[SupervisedMLRefactoringModel], refactorings: Iterable[LowLevelRefactoring], datasets: Iterable[str]):
        super().__init__(models_to_run, refactorings, datasets)

    def run(self):
        """
        The main method of this pipeline.

        For each combination of dataset, refactoring, and model, it:
        1) Retrieved the labelled instances
        2) See, _run_all_models
        """

        # if there is no datasets, refactorings, and models to run, just stop
        if not self._datasets or not self._refactorings or not self._models_to_run:
            return

        for dataset in self._datasets:
            log("Dataset {}".format(dataset))

            for refactoring in self._refactorings:
                log(f"**** Refactoring Type: refactoring.name()")

                # we have two options to select a val set,
                # 1.) Predefined in the database
                if VAL_SPLIT_SIZE < 0 and len(VALIDATION_DATASETS) > 0:
                    x_train, y_train, db_ids, scaler = retrieve_labelled_instances(
                        dataset, refactoring, True)
                    # val if any refactorings were found for the given refactoring type
                    if x_train is None:
                        log("Skip model building for refactoring type: " +
                            refactoring.name())
                        continue

                    x_val_list, y_val_list, db_ids_val_list, dataset_names = [], [], [], []
                    for validation_dataset in VALIDATION_DATASETS:
                        dataset_names.append(validation_dataset)
                        x_val, y_val, db_ids_val, _, = retrieve_labelled_instances(
                            validation_dataset, refactoring, False, scaler)
                        # val if any refactorings were found for the given refactoring type
                        if x_val is None:
                            log("Skip val set %s for refactoring type: %s" %
                                (validation_dataset, refactoring.name()))
                            continue
                        x_val_list.append(x_val)
                        y_val_list.append(y_val)
                        db_ids_val_list.append(db_ids_val)
                    if len(x_val_list) == 0:
                        log("Skip model building for refactoring type: " +
                            refactoring.name())
                        continue

                    # X and Y where already shuffled in the retrieve_labelled_instances function
                    x = pd.concat([x_train] + x_val_list)
                    y = pd.concat([y_train] + y_val_list)
                    self._run_all_models(refactoring, dataset, scaler, x, y, x_train,
                                         x_val_list, y_train, y_val_list, db_ids_val_list, dataset_names)
                # 2.) random percentage train/ val split
                else:
                    x, y, db_ids, scaler = retrieve_labelled_instances(
                        dataset, refactoring, True)
                    # val if any refactorings were found for the given refactoring type
                    if x is None:
                        log("Skip model building for refactoring type: " +
                            refactoring.name())
                        continue
                    # we split in train and val
                    # (note that we use the same split for all the models)
                    # add the db_ids to x again, in order to keep them aligned during the splitting
                    x["db_id"] = db_ids
                    x_train, x_val, y_train, y_val = train_test_split(
                        x, y, test_size=VAL_SPLIT_SIZE, random_state=42)
                    # drop the db_ids and only store the val db_ids
                    # TODO: comeup with a better wy of handling the db_ids for this case, it is quite ugly
                    x = x.drop(["db_id"], axis=1)
                    x_train = x_train.drop(["db_id"], axis=1)
                    db_ids_val = x_val["db_id"]
                    x_val = x_val.drop(["db_id"], axis=1)
                    self._run_all_models(refactoring, dataset, scaler, x, y, x_train, [
                                         x_val], y_train, [y_val], [db_ids_val], ["random split"])

    def _run_all_models(self, refactoring: LowLevelRefactoring, dataset: str, scaler, x, y, x_train, x_val_list, y_train, y_val_list, db_ids, val_names):
        """
        For each model, it:
        1) Performs the hyper parameter search
        2) Performs k-fold cross-validation
        3) Persists evaluation results and the best model
        """
        refactoring_name = refactoring.name()
        for model in self._models_to_run:
            try:
                log("\nBuilding Model {}".format(model.name()))
                self._start_time()
                trained_model = self._run_single_model(
                    model, x, y, db_ids, x_train, y_train, val_names, x_val_list, y_val_list, dataset, refactoring_name, scaler)

                # we save the best estimator we had during the search
                # Also, store the predictions with labels and db_ids, to analyze them later

                trained_model.persist_model()
                trained_model.persist_model_parameters()

                self._finish_time(dataset, model, refactoring)
            except Exception as e:
                log(
                    f"An error occurred while working on refactoring {refactoring.name()} and model {model.name()} for datasets: {str(val_names)}")
                log(str(e))
                log(str(traceback.format_exc()))
                exit(-1)

    def _run_single_model(self, trainer: SupervisedMLRefactoringModel, X: DataFrame,
                          y, db_ids, x_train: DataFrame, y_train, val_names,
                          x_val_list, y_val_list, dataset_name: str, refactoring_name: str, scaler: TransformerMixin) -> TrainedRefactoringMLModel:
        model = trainer.model()

        # perform the search for the best hyper parameters
        param_dist = trainer.params_to_tune()
        search = None

        if trainer.feature_reduction():
            features, x_train = perform_feature_reduction(
                model, x_train, y_train)
            x_val_list = [X for _, X in [
                perform_feature_reduction(model, x_val, y_val, features) for x_val, y_val in zip(x_val_list, y_val_list)]]
        else:
            features = X.columns.values

        # choose which search to apply
        if SEARCH == 'randomized':
            search = RandomizedSearchCV(model, param_dist, n_iter=N_ITER_RANDOM_SEARCH, cv=StratifiedKFold(
                n_splits=N_CV_SEARCH, shuffle=True), scoring=SCORING, n_jobs=CORE_COUNT)
        elif SEARCH == 'grid':
            search = GridSearchCV(model, param_dist, cv=StratifiedKFold(
                n_splits=N_CV_SEARCH, shuffle=True), scoring=SCORING, n_jobs=CORE_COUNT)

        log("val search started at %s\n" % now(), False)
        search.fit(x_train, y_train)
        log(format_best_parameters(search))

        training_result = TrainedRefactoringMLModel(trainer.name(
        ), dataset_name, refactoring_name, search.best_estimator_, scaler, features)

        training_result.persist_validation_prediction_results(
            db_ids, val_names, x_val_list, y_val_list)
        training_result.persist_validation_statistics(
            val_names, x_val_list, y_val_list)

        # reduce the features for the supermodel:
        if trainer.feature_reduction():
            features, X = perform_feature_reduction(model, X, y, features)

        # Run cross validation on whole dataset and save production ready model
        log("Production model build started at %s\n" % now())

        super_model = trainer.model(search.best_params_)
        super_model.fit(X, y)

        # return the scores and the best estimator
        return TrainedRefactoringMLModel(
            trainer.name(), dataset_name, refactoring_name, super_model, scaler, features)
