import os
from os import path

from configs import DATASETS, RESULTS_DIR_PATH, Level
from ml.models.builder import build_models
from ml.pipelines.binary import BinaryClassificationPipeline
from ml.refactoring import build_refactorings
from utils.log import log, log_init

"""
The main entrypoint for the binary classification procedure.

This procedure will:
    1. Fetch the data for all specified refactorings and levels, see Level and Refactorings in config.
    2. Setup the models specified models, see models/ for the model configuration and MODELS in config.
    3. Push the data through the pre-processing pipeline, initialize the classifier training, evaluate the models and store them with relevant describing data.
       See ml/pipelines/binary for more details.
"""


def main():
    log_init(path.join(RESULTS_DIR_PATH, "log", f"classifier_training_.txt"))
    log("ML4Refactoring: Binary classification")
    refactorings = build_refactorings(Level)

    # Run models
    models = build_models()
    pipeline = None

    pipeline = BinaryClassificationPipeline(
        models, refactorings, DATASETS)
    results = pipeline.run()

    return results


if __name__ == "__main__":
    main()
