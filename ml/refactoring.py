from typing import Iterable
from configs import LEVEL_MAP, Level, LEVEL_Stable_Thresholds_MAP
from db.QueryBuilder import get_level_refactorings, get_level_stable
from db.DBConnector import execute_query
from utils.log import log


class LowLevelRefactoring:
    _name = ""
    _level = Level.NONE
    _commit_threshold = -1

    def __init__(self, name: str, level: int, commit_threshold: int):
        self._name: str = name
        self._level: int = level
        self._commit_threshold: int = commit_threshold

    def get_refactored_instances(
            self,
            datasets: Iterable[str] = [],
            projects=[]):
        """
        Get all refactoring instances for this refactoring, e.g. for refactoring "Extract Method".

        Parameter:
            dataset (str) (optional): filter the refactoring instances for this dataset. If no dataset is specified, no filter is applied.
        """
        return execute_query(get_level_refactorings(
            int(self._level), self._name, datasets))

    def get_non_refactored_instances(self, datasets: Iterable[str]):
        """
        Get all non-refactored (stable) instances of the same level of the refactoring, e.g. Level 2 for refactoring "Extract Method".

        Parameter:
            dataset (str) (optional): filter the non-refactored for this dataset. If no dataset is specified, no filter is applied.
        """
        return execute_query(get_level_stable(
            int(self._level), self._commit_threshold, datasets))

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

    def commit_threshold(self) -> int:
        """
        Get the stable commit threshold for this run, e.g. 15
        """
        return self._commit_threshold


def build_refactorings(selected_level: Level):
    """
    Build LowLevelRefactoring for all refactoring types for the given level.

    Parameter:
        selected_level (Level): all level to select the refactoring types for, e.g. [Level.Class, Level.Method]
    """
    all_refactorings = []
    for level in selected_level:
        for refactoring in LEVEL_MAP[level]:
            for commit_threshold in LEVEL_Stable_Thresholds_MAP[level]:
                all_refactorings += [LowLevelRefactoring(
                    refactoring, level, commit_threshold)]
    log(f"Built refactoring objects for {str(len(all_refactorings))} refactoring types.")

    return all_refactorings
