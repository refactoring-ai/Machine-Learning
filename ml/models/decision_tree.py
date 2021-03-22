from configs import SEED
from sklearn.tree import DecisionTreeClassifier

from ml.models.base import SupervisedMLRefactoringModel


class DecisionTreeRefactoringModel(SupervisedMLRefactoringModel):
    def feature_reduction(self) -> bool:
        return False

    def params_to_tune(self):
        return {"max_depth": [3, 6, 12, 24, None],
                "max_features": ["sqrt", "log2", None],
                "min_samples_leaf": [1],
                "min_samples_split": [2],
                "splitter": ["best", "random"],
                "criterion": ["gini", "entropy"]}

    def model(self, best_params=None):
        if best_params is not None:
            return DecisionTreeClassifier(
                random_state=SEED,
                max_depth=best_params["max_depth"],
                max_features=best_params["max_features"],
                min_samples_split=best_params["min_samples_split"],
                min_samples_leaf=best_params["min_samples_leaf"],
                splitter=best_params["splitter"],
                criterion=best_params["criterion"])

        return DecisionTreeClassifier(random_state=SEED)
