from configs import DATASETS, Level, RESULTS_DIR_PATH
from db.DBConnector import close_connection
from ml.models.builder import build_models
from ml.pipelines.binary import BinaryClassificationPipeline
from ml.refactoring import build_refactorings
from utils.log import log_init, log_close, log
import datetime
from os import path


"""
The main entrypoint for the binary classification procedure.

This procedure will:
    1. Fetch the data for all specified refactorings and levels, see Level and Refactorings in config.
    2. Setup the models specified models, see models/ for the model configuration and MODELS in config.
    3. Push the data through the pre-processing pipeline, initialize the classifier training, evaluate the models and store them with relevant describing data.
       See ml/pipelines/binary for more details. 
"""

log_init(path.join(RESULTS_DIR_PATH, "results", f"classifier_training_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"))
log("ML4Refactoring: Binary classification")

refactorings = build_refactorings(Level)

# Run models
models = build_models()
pipeline = None

pipeline = BinaryClassificationPipeline(models, refactorings, DATASETS)
pipeline.run()

# That's it, folks.
log_close()
close_connection()

exit()