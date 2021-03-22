import traceback
from typing import Dict, Iterable

import pandas as pd
from sklearn.utils import shuffle
from configs import (
    CORE_COUNT,
    DATASETS,
    N_CV_SEARCH,
    N_ITER_RANDOM_SEARCH,
    SCORING,
    SEARCH,
    SEED,
    VAL_SPLIT_SIZE,
    VALIDATION_DATASETS)
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
from utils.date_utils import windows_path_friendly_now


class BinaryClassificationPipeline(MLPipeline):
    """
    Train models for binary classification
    """

    def __init__(
            self,
            models_to_run: Iterable[SupervisedMLRefactoringModel],
            refactorings: Iterable[LowLevelRefactoring],
            datasets: Iterable[str]):
        super().__init__(models_to_run, refactorings, datasets)

    def run(self, projects: Iterable[str] = [], val_proj=[]):
        """
        The main method of this pipeline.

        For each combination of dataset, refactoring, and model, it:
        1) Retrieved the labelled instances
        2) See, _run_all_models
        """
        results = []
        # if there is no datasets, refactorings, and models to run, just stop
        if not self._datasets or not self._refactorings or not self._models_to_run:
            return

        for refactoring in self._refactorings:
            log(f"**** Refactoring Type: {refactoring.name()}")
            # we have two options to select a val set,
            # 1.) Predefined in the database
            if (VAL_SPLIT_SIZE < 0 and len(VALIDATION_DATASETS)
                    > 0) or len(val_proj) >= 1:
                # for dataset in self._datasets:
                #     log("Dataset {}".format(dataset))
                print(f'getting training data for projects {projects}')
                x_train, y_train, scaler = retrieve_labelled_instances(
                    DATASETS, refactoring, True)

                # val if any refactorings were found for the given refactoring
                # type

                if x_train is None:
                    log("Skip model building for refactoring type: " +
                        refactoring.name())
                    continue
                x_train, y_train = shuffle(x_train, y_train, random_state=SEED)
                x_val_list, y_val_list, db_ids_val_list, dataset_names = [], [], [], []
                if len(val_proj) >= 1:
                    print(f'getting val data for project {val_proj}')
                    x_val, y_val, _, = retrieve_labelled_instances(
                        "industry", refactoring, False, scaler, projects=val_proj)
                    print(f"val_len")
                    if x_val is None:
                        log("Skip val set %s for refactoring type: %s" %
                            (val_proj[0], refactoring.name()))
                        continue
                    x_val, y_val = shuffle(x_val, y_val, random_state=SEED)

                    dataset_names.append(val_proj[0])

                    x_val_list.append(x_val)
                    y_val_list.append(y_val)
                else:
                    for validation_dataset in VALIDATION_DATASETS:
                        dataset_names.append(validation_dataset)
                        x_val, y_val, _, = retrieve_labelled_instances(
                            validation_dataset, refactoring, False, scaler, projects=projects)
                        # val if any refactorings were found for the given
                        # refactoring type
                        if x_val is None:
                            log("Skip val set %s for refactoring type: %s" %
                                (validation_dataset, refactoring.name()))
                            continue
                        x_val, y_val = shuffle(x_val, y_val, random_state=SEED)
                        x_val_list.append(x_val)
                        y_val_list.append(y_val)
                if len(x_val_list) == 0:
                    log("Skip model building for refactoring type: " +
                        refactoring.name())
                    continue
                    # X and Y where already shuffled in the
                    # retrieve_labelled_instances function

                x = pd.concat([x_train] + x_val_list)
                y = pd.concat([y_train] + y_val_list)
                results.append(
                    self._run_all_models(
                        refactoring,
                        scaler,
                        x,
                        y,
                        x_train,
                        x_val_list,
                        y_train,
                        y_val_list,
                        dataset_names))
            # 2.) random percentage train/ val split
            else:
                x, y, scaler = retrieve_labelled_instances(
                    DATASETS, refactoring, True)
                # val if any refactorings were found for the given refactoring
                # type
                if x is None:
                    log("Skip model building for refactoring type: " +
                        refactoring.name())
                    continue
                # we split in train and val
                # (note that we use the same split for all the models)
                # add the db_ids to x again, in order to keep them aligned during the splitting
                # x["db_id"] = db_ids

                x_train, x_val, y_train, y_val = train_test_split(
                    x, y, test_size=VAL_SPLIT_SIZE, random_state=SEED, stratify=y)
                results.append(
                    self._run_all_models(
                        refactoring,
                        scaler,
                        x,
                        y,
                        x_train,
                        [x_val],
                        y_train,
                        [y_val],
                        ["random split"]))
        return results

    def _run_all_models(
            self,
            refactoring: LowLevelRefactoring,
            scaler,
            X,
            y,
            x_train,
            x_val_list,
            y_train,
            y_val_list,
            val_names):
        """
        For each model, it:
        1) Performs the hyper parameter search
        2) Performs k-fold cross-validation
        3) Persists evaluation results and the best model
        """
        results = {}
        refactoring_name = refactoring.name()
        for model in self._models_to_run:
            try:
                log("\nBuilding Model {}".format(model.name()))
                self._start_time()
                production_model, trained_model = self._run_single_model(
                    model, X, y, x_train, y_train, val_names, x_val_list, y_val_list, refactoring_name, scaler, refactoring.commit_threshold())

                # we save the best estimator we had during the search
                # Also, store the predictions with labels and db_ids, to
                # analyze them later

                self._finish_time(model, refactoring)
                results[model.name()] = production_model, trained_model
            except Exception as e:
                log(
                    f"An error occurred while working on refactoring {refactoring.name()} and model {model.name()} for datasets: {str(val_names)}")
                log(str(e))
                log(str(traceback.format_exc()))
                exit(-1)
        return results

    def _run_single_model(
            self,
            trainer: SupervisedMLRefactoringModel,
            X: DataFrame,
            y,
            x_train: DataFrame,
            y_train,
            val_names,
            x_val_list,
            y_val_list,
            refactoring_name: str,
            scaler: TransformerMixin,
            commit_threshold: int) -> TrainedRefactoringMLModel:
        model = trainer.model()

        # perform the search for the best hyper parameters
        param_dist = trainer.params_to_tune()
        search = None

        if trainer.feature_reduction():
            features, x_train = perform_feature_reduction(
                model, x_train, y_train)
            x_val_list = [
                X for _, X in [
                    perform_feature_reduction(
                        model, x_val, y_val, features) for x_val, y_val in zip(
                        x_val_list, y_val_list)]]
        else:
            features = X.columns.values

        # choose which search to apply
        if SEARCH == 'randomized':
            search = RandomizedSearchCV(
                model,
                param_dist,
                n_iter=N_ITER_RANDOM_SEARCH,
                cv=StratifiedKFold(
                    n_splits=N_CV_SEARCH,
                    shuffle=True),
                scoring=SCORING,
                n_jobs=CORE_COUNT,
                verbose=1)
        elif SEARCH == 'grid':
            search = GridSearchCV(
                model,
                param_dist,
                cv=StratifiedKFold(
                    n_splits=N_CV_SEARCH,
                    shuffle=True),
                scoring=SCORING,
                n_jobs=CORE_COUNT,
                verbose=1)

        log("val search started at %s\n" % now())

        log(
            f'train size = {len(x_train.index)}\ntest size = {len(x_val_list[0].index)}')

        search.fit(x_train, y_train)
        log(format_best_parameters(search))
        windows_path_friendly_timestamp = windows_path_friendly_now()
        training_model = TrainedRefactoringMLModel(
            trainer.name(),
            self.datasets_str(),
            refactoring_name,
            search.best_estimator_,
            scaler,
            features,
            windows_path_friendly_timestamp,
            commit_threshold,
            False,
            trainer.feature_reduction())

        training_model.persist_model_parameters(),

        training_model.persist_validation_statistics(
            val_names, x_val_list, y_val_list)
        training_model.persist_model(),
        # reduce the features for the supermodel:
        if trainer.feature_reduction():
            features, X = perform_feature_reduction(model, X, y, features)
        # Run cross validation on whole dataset and save production ready model
        log("Production model build started at %s\n" % now())
        production_model = trainer.model(search.best_params_)
        production_model.fit(X, y)
        # return the scores and the best estimator
        production_model = TrainedRefactoringMLModel(
            trainer.name(), '-'.join(self._datasets),
            refactoring_name, production_model, scaler,
            features, windows_path_friendly_timestamp,
            commit_threshold, True, trainer.feature_reduction())
        production_model.persist_model()
        production_model.persist_model_parameters()
        return production_model, training_model
