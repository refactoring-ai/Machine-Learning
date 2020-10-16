import datetime
from configs import RESULTS_DIR_PATH
from utils.classifier_utils import store_json, store_joblib, store_collection
from os import path


class MLModel(object):
    def name(self):
        return type(self).__name__

    def persist(self, dataset, refactoring_name, k, features, model_obj, scaler_obj, test_results=None, test_names=None, formatted_results=None):
        """
        Persist this model with reference to its dataset, refactoring_type, features, model
        and if specified also the prediction results for the validation sets.
        """
        pass

    def _save_scaler(self, dataset, refactoring_name, k, scaler_obj):
        file_name = path.join(RESULTS_DIR_PATH, "results", "scaler", f"scaler_{self.name()}_{dataset}_{refactoring_name.replace(' ', '')}_K{k}_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.joblib")
        store_joblib(scaler_obj, file_name)

    def _save_features(self, dataset, refactoring_name, k, features):
        feature_path = path.join(RESULTS_DIR_PATH, "results", "model", f"features_{self.name()}_{dataset}_{refactoring_name.replace(' ', '')}_K{k}_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv")
        store_collection(features, feature_path)

    def _save_validation_results(self, dataset, refactoring_name, k, test_results, test_names, formatted_results):
        for index, test_result in enumerate(test_results):
            results_path = path.join(RESULTS_DIR_PATH, "results", "predictions", f"predictions_{self.name()}_{dataset}_{test_names[index]}_{refactoring_name.replace(' ', '')}_K{k}_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json")
            data = {
                'test_scores': formatted_results,
                'test_results': test_result.to_json()
            }
            store_json(data, results_path)


class SupervisedMLRefactoringModel(MLModel):
    """
    Represents all supervised ML models.

    They all must have 3 features:
    - params_to_tune: A dictionary with the list of parameters and values for the hyperparameter search.
    - model: Returns a new model. If params is passed, with the configured params.
    - persist: Persists the best found estimator as well as the final model.
    - feature_reduction: Should we perform feature reduction for this model?

    Note: Whenever you create a new model, do not forget to add it to `builder.py`.
    """
    def feature_reduction(self) -> bool:
        pass

    def params_to_tune(self):
        pass

    def model(self, best_params=None):
        pass

    def persist(self, dataset, refactoring_name, k, features, model_obj, scaler_obj,
                test_results=None, test_names=None, formatted_results=None):
        """
        Persist this model with reference to its dataset, refactoring_type, features, model
        and if specified also the prediction results for the validation sets.
        """
        model_path = path.join(RESULTS_DIR_PATH, "results", "model", f"model_{self.name()}_{dataset}_{refactoring_name.replace(' ', '')}_K{k}_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.joblib")
        store_joblib(model_obj, model_path)

        self._save_scaler(dataset, refactoring_name, k, scaler_obj)
        self._save_features(dataset, refactoring_name, k, features)
        if test_results is not None and test_names is not None and formatted_results is not None:
            self._save_validation_results(dataset, refactoring_name, k, test_results, test_names, formatted_results)