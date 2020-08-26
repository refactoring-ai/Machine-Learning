from sklearn.ensemble import ExtraTreesClassifier

from configs import CORE_COUNT
from ml.models.base import SupervisedMLRefactoringModel


class ExtraTreeRefactoringModel(SupervisedMLRefactoringModel):
    def params_to_tune(self):
        return {"max_depth": [3, 6, 12, 24],
                  "max_leaf_nodes": [2, 3, 5, 6, 10, None],
                  "max_features": ["sqrt", "log2", None],
                  "min_samples_split": [2, 3, 4, 5, 10],
                  "min_samples_leaf": [1, 2, 3, 4, 5, 10],
                  "bootstrap": [True, False],
                  "criterion": ["gini", "entropy"],
                  "n_estimators": [10, 50, 100, 150, 200]}

    def model(self, best_params=None):
        if best_params is not None:
            return ExtraTreesClassifier(random_state=42,
                                        max_depth=best_params["max_depth"],
                                        max_leaf_nodes=best_params["max_leaf_nodes"],
                                        max_features=best_params["max_features"],
                                        min_samples_split=best_params["min_samples_split"],
                                        min_samples_leaf=best_params["min_samples_leaf"],
                                        bootstrap=best_params["bootstrap"],
                                        criterion=best_params["criterion"],
                                        n_estimators=best_params["n_estimators"],
                                        n_jobs=CORE_COUNT)

        return ExtraTreesClassifier(random_state=42)

