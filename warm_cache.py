from configs import DATASETS, Level, VALIDATION_DATASETS, LEVEL_Stable_Thresholds_MAP, CACHE_DIR_PATH, LEVEL_MAP
from db.QueryBuilder import get_level_stable, get_level_refactorings_count, get_level_refactorings
from db.DBConnector import execute_query, close_connection
from utils.log import log_init, log_close, log
import time
import datetime
from os import path


"""
The amount of samples for refactorings and non-refactorings in the database is enormous, thus caching the relevant data on your local machine can speed up the machine learning process.

This class fetches the training data for refactoring instances and non-refactoring instances, as configured, from the database and stores the results of the queries in cache files. 

Note:
    In order to use this feature, ensure in the USE_CACHE is enabled in the config.
"""

log_init(path.join(CACHE_DIR_PATH, "results", f"warm-up_cache_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"))
log('Begin cache warm-up')
start_time = time.time()

for dataset in (DATASETS + VALIDATION_DATASETS):
    log("\n**** dataset: " + dataset)
    for level in [Level.Class, Level.Method, Level.Variable, Level.Field]:
        log("-- non refactored instances for " + str(level))
        non_refactored = execute_query(get_level_stable(int(level), LEVEL_Stable_Thresholds_MAP[level], dataset))
        log(str(len(non_refactored)) + " non-refactored instances were found for level: " + str(level))

        log("-- " + str(level) + " refactoring types with count")
        refactorings = execute_query(get_level_refactorings_count(int(level), dataset))
        log(refactorings.to_string())
        for refactoring_name in refactorings['refactoring']:
            execute_query(get_level_refactorings(int(level), refactoring_name, dataset))

log('Cache warm-up took %s seconds.' % (time.time() - start_time))
log_close()
close_connection()

exit()