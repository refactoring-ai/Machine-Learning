from sklearn.ensemble import RandomForestClassifier

from configs import CORE_COUNT
from ml.models.base import SupervisedMLRefactoringModel


class RandomForestRefactoringModel(SupervisedMLRefactoringModel):
    def feature_reduction(self) -> bool:
        return False

    def params_to_tune(self):
        return {"max_depth": [None],
                  "max_features": ["auto", "log2", None],
                  "min_samples_split": [2, 3, 4, 5],
                  "bootstrap": [True, False],
                  "criterion": ["gini", "entropy"],
                  "n_estimators": [50, 100, 150, 200]}

    def model(self, best_params=None):
        if best_params is not None:
            return RandomForestClassifier(random_state=42, n_jobs=CORE_COUNT,
                                          max_depth=best_params["max_depth"],
                                          max_features=best_params["max_features"],
                                          min_samples_split=best_params["min_samples_split"],
                                          bootstrap=best_params["bootstrap"],
                                          criterion=best_params["criterion"],
                                          n_estimators=best_params["n_estimators"])

        return RandomForestClassifier(random_state=42)


class RandomForestFastRefactoringModel(SupervisedMLRefactoringModel):
    """
    A faster simpler configuration of the random forest classifier. This will return quick results, with (hopefully) slightly reduced accuracy.
    """
    def feature_reduction(self) -> bool:
        return False

    def params_to_tune(self):
        return {"max_depth": [3, 12, 24],
                "max_features": ["auto", "log2"],
                "min_samples_split": [2, 5, 10],
                "bootstrap": [True, False],
                "criterion": ["gini", "entropy"],
                "n_estimators": [10, 100, 150, 200]}


    def model(self, best_params=None):
        if best_params is not None:
            return RandomForestClassifier(random_state=42, n_jobs=CORE_COUNT,
                                          max_depth=best_params["max_depth"],
                                          max_features=best_params["max_features"],
                                          min_samples_split=best_params["min_samples_split"],
                                          bootstrap=best_params["bootstrap"],
                                          criterion=best_params["criterion"],
                                          n_estimators=best_params["n_estimators"])

        return RandomForestClassifier(random_state=42)
