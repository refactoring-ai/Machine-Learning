import traceback
import pandas as pd
from configs import SEARCH, N_CV_SEARCH, N_ITER_RANDOM_SEARCH, VAL_SPLIT_SIZE, VALIDATION_DATASETS, TEST, CORE_COUNT, \
    SCORING
from ml.preprocessing.feature_reduction import perform_feature_reduction
from utils.classifier_utils import format_results_single_run, evaluate_model
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, GridSearchCV, train_test_split
from ml.pipelines.pipelines import MLPipeline
from ml.preprocessing.preprocessing import retrieve_labelled_instances
from utils.classifier_utils import format_best_parameters
from utils.date_utils import now
from utils.log import log


def _build_production_model(model_def, best_params, x, y):
    log("Production model build started at %s\n" % now())

    super_model = model_def.model(best_params)
    super_model.fit(x, y)

    return super_model


class BinaryClassificationPipeline(MLPipeline):
    """
    Train models for binary classification
    """

    def __init__(self, models_to_run, refactorings, datasets):
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
                refactoring_name = refactoring.name()
                log("**** Refactoring Type: %s" % refactoring_name)

                # we have two options to select a val set,
                # 1.) Predefined in the database
                if VAL_SPLIT_SIZE < 0 and len(VALIDATION_DATASETS) > 0:
                    x_train, y_train, db_ids, scaler = retrieve_labelled_instances(dataset, refactoring, True)
                    # val if any refactorings were found for the given refactoring type
                    if x_train is None:
                        log("Skip model building for refactoring type: " + refactoring.name())
                        continue

                    x_val_list, y_val_list, db_ids_val_list, dataset_names = [], [], [], []
                    for validation_dataset in VALIDATION_DATASETS:
                        dataset_names.append(validation_dataset)
                        x_val, y_val, db_ids_val, _, = retrieve_labelled_instances(validation_dataset, refactoring, False, scaler)
                        # val if any refactorings were found for the given refactoring type
                        if x_val is None:
                            log("Skip val set %s for refactoring type: %s" % (validation_dataset, refactoring.name()))
                            continue
                        x_val_list.append(x_val)
                        y_val_list.append(y_val)
                        db_ids_val_list.append(db_ids_val)
                    if len(x_val_list) == 0:
                        log("Skip model building for refactoring type: " + refactoring.name())
                        continue

                    # X and Y where already shuffled in the retrieve_labelled_instances function
                    x = pd.concat([x_train] + x_val_list)
                    y = pd.concat([y_train] + y_val_list)
                    self._run_all_models(refactoring, refactoring_name, dataset, scaler, x, y, x_train,
                                         x_val_list, y_train, y_val_list, db_ids_val_list, dataset_names)
                # 2.) random percentage train/ val split
                else:
                    x, y, db_ids, scaler = retrieve_labelled_instances(dataset, refactoring, True)
                    # val if any refactorings were found for the given refactoring type
                    if x is None:
                        log("Skip model building for refactoring type: " + refactoring.name())
                        continue
                    # we split in train and val
                    # (note that we use the same split for all the models)
                    # add the db_ids to x again, in order to keep them aligned during the splitting
                    x["db_id"] = db_ids
                    x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=VAL_SPLIT_SIZE, random_state=42)
                    # drop the db_ids and only store the val db_ids
                    #TODO: comeup with a better wy of handling the db_ids for this case, it is quite ugly
                    x = x.drop(["db_id"], axis=1)
                    x_train = x_train.drop(["db_id"], axis=1)
                    db_ids_val = x_val["db_id"]
                    x_val = x_val.drop(["db_id"], axis=1)
                    self._run_all_models(refactoring, refactoring_name, dataset, scaler, x, y, x_train, [x_val], y_train, [y_val], [db_ids_val], ["random split"])


    def _run_all_models(self, refactoring, refactoring_name, dataset, scaler, x, y, x_train, x_val_list, y_train, y_val_list, db_ids, val_names):
        """
        For each model, it:
        1) Performs the hyper parameter search
        2) Performs k-fold cross-validation
        3) Persists evaluation results and the best model
        """
        for model in self._models_to_run:
            model_name = model.name()
            if TEST:
                model_name += " val"
            try:
                log("\nBuilding Model {}".format(model.name()))
                self._start_time()
                features, val_scores, val_results, model_to_save, search = self._run_single_model(model, x, y, x_train, x_val_list, y_train, y_val_list, db_ids)

                # log val scores
                formatted_results = format_results_single_run(dataset, refactoring_name, val_names, model_name, val_scores["f1_score"], val_scores["precision"],
                                                              val_scores["recall"], val_scores['accuracy'], val_scores['tn'],
                                                              val_scores['fp'], val_scores['fn'], val_scores['tp'], val_scores["permutation_importance"],
                                                              model_to_save, features, format_best_parameters(search))
                log(formatted_results)

                # we save the best estimator we had during the search
                # Also, store the predictions with labels and db_ids, to analyze them later
                model.persist(dataset, refactoring_name, features, model_to_save, scaler,
                              val_results, val_names, formatted_results)
                self._finish_time(dataset, model, refactoring)
            except Exception as e:
                log("An error occurred while working on refactoring " + refactoring_name + " model " + model.name()
                    + " with datasets: " + str(val_names))
                log(str(e))
                log(str(traceback.format_exc()))


    def _run_single_model(self, model_def, X, y, x_train, x_val_list, y_train, y_val_list, db_ids):
        model = model_def.model()

        # perform the search for the best hyper parameters
        param_dist = model_def.params_to_tune()
        search = None

        # choose which search to apply
        if SEARCH == 'randomized':
            search = RandomizedSearchCV(model, param_dist, n_iter=N_ITER_RANDOM_SEARCH, cv=StratifiedKFold(n_splits=N_CV_SEARCH, shuffle=True), scoring=SCORING, n_jobs=CORE_COUNT)
        elif SEARCH == 'grid':
            search = GridSearchCV(model, param_dist, cv=StratifiedKFold(n_splits=N_CV_SEARCH, shuffle=True), scoring=SCORING, n_jobs=CORE_COUNT)

        if model_def.feature_reduction():
            features, x_train = perform_feature_reduction(search, x_train, y_train)
            x_val_list = [X for _, X in [perform_feature_reduction(search, x_val, y_val, features) for x_val, y_val in zip(x_val_list, y_val_list)]]
        else:
            features = X.columns.values

        # Train and evaluate the model
        trained_model = self.train_model(search, x_train, y_train, )
        val_scores, val_results = evaluate_model(trained_model, x_val_list, y_val_list, db_ids)

        # reduce the features for the supermodel:
        if model_def.feature_reduction():
            features, X = perform_feature_reduction(search, X, y, features)
        # Run cross validation on whole dataset and safe production ready model
        super_model = _build_production_model(model_def, search.best_params_, X, y)

        # return the scores and the best estimator
        return features, val_scores, val_results, super_model, search


    def train_model(self, search, x_train, y_train):
        log("val search started at %s\n" % now(), False)
        search.fit(x_train, y_train)
        log(format_best_parameters(search))
        return search.best_estimator_