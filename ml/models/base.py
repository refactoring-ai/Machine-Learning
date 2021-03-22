from abc import ABC, abstractmethod
from typing import Dict

from sklearn.base import BaseEstimator


class MLModel(ABC):
    def name(self) -> str:
        return type(self).__name__

    def path_friendly_name(self) -> str:
        return self.name().replace(" ", "-")


class SupervisedMLRefactoringModel(MLModel):
    """
    Represents all supervised ML models.

    They all must have 3 features:
    - params_to_tune: A dictionary with the list of parameters
     and values for the hyperparameter search.
    - model: Returns a new model.
    If params is passed, with the configured params.
    - persist: Persists the best found estimator as well as the final model.
    - feature_reduction: Should we perform feature reduction for this model?

    Note: Whenever you create a new model,
    do not forget to add it to `builder.py`.
    """

    @abstractmethod
    def feature_reduction(self) -> bool:
        ...

    @abstractmethod
    def params_to_tune(self) -> Dict[str, any]:
        ...

    @abstractmethod
    def model(self, params: Dict[str, any] = None) -> BaseEstimator:
        ...
