from configs import DATASETS, Level
from db.DBConnector import close_connection
from ml.models.builder import build_models
from ml.pipelines.binary import BinaryClassificationPipeline
from ml.refactoring import build_refactorings
from utils.log import log_init, log_close, log
import datetime

log_init(f"results/classifier_training_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt")
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