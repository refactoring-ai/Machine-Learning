from configs import DATASETS, Level, VALIDATION_DATASETS, CACHE_DIR_PATH, LEVEL_MAP
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

for dataset in [""] + DATASETS + VALIDATION_DATASETS:
    for level in [Level.Class, Level.Method, Level.Variable, Level.Field, Level.Other]:
        log(f"-- non refactored instances for {level} for dataset: {dataset}")
        for k in [15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]:
            log(f"---- non refactored instances with k {k} for {level} for dataset: {dataset}")
            non_refactored = execute_query(get_level_stable(int(level), k, dataset))
            log(str(len(non_refactored)) + " non-refactored instances were found for level: " + str(level))

        log(f"-- {level} refactoring types with count for dataset: {dataset}")
        refactorings = execute_query(get_level_refactorings_count(int(level), dataset))
        log(refactorings.to_string())
        for refactoring_name in LEVEL_MAP[level]:
            log(f"---- {refactoring_name} for dataset: {dataset}")
            execute_query(get_level_refactorings(int(level), refactoring_name, dataset))


log('Cache warm-up took %s seconds.' % (time.time() - start_time))
log_close()
close_connection()

exit()