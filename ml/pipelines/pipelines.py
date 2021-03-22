from ml.refactoring import LowLevelRefactoring
from typing import Iterable
from utils.date_utils import now
from utils.log import log


class MLPipeline:
    """
    Represents a generic pipeline.

    The `run` method is the one that does the magic. Other methods mostly support logging.
    """

    def __init__(
            self,
            models_to_run,
            refactorings: Iterable[LowLevelRefactoring],
            datasets: Iterable[str]):
        self._models_to_run = models_to_run
        self._refactorings: Iterable[LowLevelRefactoring] = refactorings
        self._datasets: Iterable[str] = datasets
        self._start_datetime = None
        self.start_pipeline_date_time: str = now()
        self._current_execution_number: int = 0

    def _finish_time(self, model, refactoring):
        finish_hour = now()
        log("Finished at %s" % finish_hour)
        log(("TIME,%s,%s,%s,%s" % (refactoring.name(),
                                   model.name(), self._start_datetime, finish_hour)))

    def _start_time(self):
        self._count_execution()
        self._start_hour = now()
        log("Started at %s" % self._start_hour)

    def _total_number_of_executions(self):
        return len(self._models_to_run) * \
            len(self._refactorings) * len(self._datasets)

    def _count_execution(self):
        self._current_execution_number = self._current_execution_number + 1
        log("Execution: {}/{}".format(self._current_execution_number,
                                      self._total_number_of_executions()))

    def datasets_str(self) -> str:
        return "-".join(self._datasets)
