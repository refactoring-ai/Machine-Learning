from configs import SEED
from random import uniform

from sklearn.svm import SVC, LinearSVC

from ml.models.base import SupervisedMLRefactoringModel


class LinearSVMRefactoringModel(SupervisedMLRefactoringModel):
    def feature_reduction(self) -> bool:
        return False

    def params_to_tune(self):
        C = [1.0] + [uniform(0.01, 10) for i in range(0, 5)]
        return {"C": C,
                "penalty": ["l1", "l2"],
                "loss": ["hinge", "squared_hinge"],
                "dual": [False],
                "tol": [1e-04]
                }

    def model(self, best_params=None):
        if best_params is not None:
            return LinearSVC(dual=best_params["dual"], C=best_params["C"],
                             penalty=best_params["penalty"],
                             loss=best_params["loss"],
                             tol=best_params["tol"],
                             random_state=SEED)

        return LinearSVC(random_state=SEED)


class NonLinearSVMRefactoringModel(SupervisedMLRefactoringModel):
    def feature_reduction(self) -> bool:
        return False

    def params_to_tune(self):
        return {"C": [uniform(0.01, 10) for i in range(0, 4)],
                "kernel": ["poly", "rbf", "sigmoid"],
                "degree": [2, 3, 5, 7, 10],
                "gamma": [uniform(0.01, 10) for i in range(0, 4)],
                "decision_function_shape": ["ovo", "ovr"]}

    def model(self, best_params=None):
        if best_params is not None:
            return SVC(
                C=best_params["C"],
                kernel=best_params["kernel"],
                degree=best_params["degree"],
                gamma=best_params["gamma"],
                decision_function_shape=best_params["decision_function_shape"])

        return SVC(shrinking=False)
