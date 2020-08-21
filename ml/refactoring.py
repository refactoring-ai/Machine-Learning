from configs import LEVEL_MAP, LEVEL_Stable_Thresholds_MAP, Level
from db.QueryBuilder import get_level_refactorings, get_all_level_stable
from db.DBConnector import execute_query
from utils.log import log


class LowLevelRefactoring:
    _name = ""
    _level = Level.NONE

    def __init__(self, name, level):
        self._name = name
        self._level = level

    def get_refactored_instances(self, dataset: str = ""):
        """
        Get all refactoring instances for this refactoring, e.g. for refactoring "Extract Method".

        Parameter:
            dataset (str) (optional): filter the refactoring instances for this dataset. If no dataset is specified, no filter is applied.
        """
        return execute_query(get_level_refactorings(int(self._level), self._name, dataset))

    def get_non_refactored_instances(self, dataset: str = ""):
        """
        Get all non-refactored (stable) instances of the same level of the refactoring, e.g. Level 2 for refactoring "Extract Method".

        Parameter:
            dataset (str) (optional): filter the non-refactored for this dataset. If no dataset is specified, no filter is applied.
        """
        return execute_query(get_all_level_stable(int(self._level), LEVEL_Stable_Thresholds_MAP[self._level], dataset))

    def level(self) -> str:
        """
        Get the level of the refactoring type, e.g. Level.Field for "Push Down Attribute"
        """
        return str(self._level)

    def name(self) -> str:
        """
        Get the name of the refactoring type, e.g. "Push Down Attribute"
        """
        return self._name


def build_refactorings(selected_level: Level):
    """
    Build LowLevelRefactoring for all refactoring types for the given level.

    Parameter:
        selected_level (Level): all level to select the refactoring types for, e.g. [Level.Class, Level.Method]
    """
    all_refactorings = []
    for level in selected_level:
        for refactoring in LEVEL_MAP[level]:
            all_refactorings += [LowLevelRefactoring(refactoring, level)]
    log(f"Built refactoring objects for {str(len(all_refactorings))} refactoring types.")

    return all_refactorings