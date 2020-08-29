from collections import Counter
import pandas as pd
from configs import SCALE_DATASET, BALANCE_DATASET, DROP_METRICS, \
    DROP_PROCESS_AND_AUTHORSHIP_METRICS, PROCESS_AND_AUTHORSHIP_METRICS, DROP_FAULTY_PROCESS_AND_AUTHORSHIP_METRICS, \
    TRAINING_SAMPLE_FRACTION_POSITIVE, TRAINING_SAMPLE_FRACTION_NEGATIVE, EVALUATION_SAMPLE_FRACTION, MIN_TRAINING_SAMPLE_COUNT_POSITIVE, MIN_TRAINING_SAMPLE_COUNT_NEGATIVE, MIN_EVALUATION_SAMPLE_COUNT
from ml.preprocessing.sampling import perform_balancing, sample_reduction
from ml.preprocessing.scaling import perform_scaling, perform_fit_scaling
from ml.refactoring import LowLevelRefactoring
from utils.log import log
from sklearn.utils import shuffle


def retrieve_labelled_instances(dataset, refactoring: LowLevelRefactoring, is_training_data: bool = True, scaler=None):
    """
    This method retrieves all the labelled instances for a given refactoring and dataset.
    It performs the following pipeline:
      1. Get all refactored and non refactored instances from the db.
      2. Merge them into a single dataset, having 1=true and 0=false, as labels.
      3. Removes possible NAs (the data collection process is tough; bad data might had make it through)
      4. Shuffles the dataset (good practice)
      5. Balances the dataset (if configured)
      6. Scales the features values (if configured)

    :param dataset: a string containing the name of the dataset to be retrieved
    :param refactoring: the refactoring object, containing the refactoring to be retrieved
    :param is_training_data: is this training data? If so,
    :param scaler: a predefined scaler, for this data

    :return:
        x: a dataframe with the feature values
        y: the label (1=true, a refactoring has happened, 0=false, no refactoring has happened)
        ids: instance ids, to query the actual data from the database
        scaler: the scaler object used in the scaling process.
    """
    log("---- Retrieve labeled instances for dataset: %s" % dataset)

    # get all refactoring examples we have in our dataset
    refactored_instances = refactoring.get_refactored_instances(dataset)
    # load non-refactoring examples
    non_refactored_instances = refactoring.get_non_refactored_instances(dataset)

    log("raw number of refactoring instances: {}".format(refactored_instances.shape[0]), False)
    log("raw number of non-refactoring instances: {}".format(non_refactored_instances.shape[0]), False)

    # if there' still a row with NAs, drop it as it'll cause a failure later on.
    refactored_instances = refactored_instances.dropna()
    non_refactored_instances = non_refactored_instances.dropna()

    # test if any refactorings were found for the given refactoring type
    if refactored_instances.shape[0] == 0:
        log("No refactorings found for refactoring type: " + refactoring.name())
        return None, None, None, None
    # test if any refactorings were found for the given refactoring type
    if non_refactored_instances.shape[0] == 0:
        log("No non-refactorings found for refactoring type: " + refactoring.name())
        return None, None, None, None

    log("refactoring instances (after dropping NA)s: {}".format(refactored_instances.shape[0]), False)
    log("non-refactoring instances (after dropping NA)s: {}".format(non_refactored_instances.shape[0]), False)

    assert non_refactored_instances.shape[0] > 0, "Found no non-refactoring instances for level: " + refactoring.level()

    # set the prediction variable as true and false in the datasets
    refactored_instances["prediction"] = 1
    non_refactored_instances["prediction"] = 0

    # reduce the amount training samples, if specified, also keep the specified balance
    if is_training_data and TRAINING_SAMPLE_FRACTION_NEGATIVE < 1:
        non_refactored_instances = sample_reduction(non_refactored_instances, TRAINING_SAMPLE_FRACTION_NEGATIVE, MIN_TRAINING_SAMPLE_COUNT_NEGATIVE)
    if is_training_data and TRAINING_SAMPLE_FRACTION_POSITIVE < 1:
        refactored_instances = sample_reduction(refactored_instances, TRAINING_SAMPLE_FRACTION_POSITIVE, MIN_TRAINING_SAMPLE_COUNT_POSITIVE)
    # reduce the amount evaluation samples, if specified
    if not is_training_data and EVALUATION_SAMPLE_FRACTION < 1:
        refactored_instances = sample_reduction(refactored_instances, EVALUATION_SAMPLE_FRACTION, MIN_EVALUATION_SAMPLE_COUNT)
        non_refactored_instances = sample_reduction(non_refactored_instances, EVALUATION_SAMPLE_FRACTION, MIN_EVALUATION_SAMPLE_COUNT)


    # now, combine both datasets (with both TRUE and FALSE predictions)
    if non_refactored_instances.shape[1] != refactored_instances.shape[1]:
        raise ImportError("Number of columns differ from both datasets.")
    merged_dataset = pd.concat([refactored_instances, non_refactored_instances], ignore_index=True)

    # do we want to try the models without some metrics, e.g. process and authorship metrics?
    merged_dataset = merged_dataset.drop(DROP_METRICS, axis=1)

    #Remove all instances with a -1 value in the process and authorship metrics,
    # ToDo: do this after the feature reduction to simplify the query and do not drop instances which are not affected by faulty process and authorship metrics, which are not in the feature set
    if DROP_FAULTY_PROCESS_AND_AUTHORSHIP_METRICS and not DROP_PROCESS_AND_AUTHORSHIP_METRICS:
        log("Instance count before dropping faulty process metrics: {}".format(len(merged_dataset.index)), False)
        metrics = [metric for metric in PROCESS_AND_AUTHORSHIP_METRICS if metric in merged_dataset.columns.values]
        query = " and ".join(["%s != -1" % metric for metric in metrics])
        merged_dataset = merged_dataset.query(query)
        log("Instance count after dropping faulty process metrics: {}".format(len(merged_dataset.index)), False)

    # separate the x from the y (as required by the scikit-learn API)
    x = merged_dataset.drop("prediction", axis=1)
    y = merged_dataset["prediction"]

    # balance the datasets, as we have way more 'non refactored examples' rather than refactoring examples
    # for now, we basically perform under sampling
    if is_training_data and BALANCE_DATASET:
        log("instances before balancing: {}".format(Counter(y)), False)
        x, y = perform_balancing(x, y)
        assert x.shape[0] == y.shape[0], "Balancing did not work, x and y have different shapes."
        log("instances after balancing: {}".format(Counter(y)), False)

    # shuffle data after balancing it, because some of the samplers order the data during balancing it
    x, y = shuffle(x, y)

    # also save the instance ids, we will need them later to analyse the classifier results, but we don't won't to scale them nor drop them during feature reduction
    ids = x["db_id"]
    x = x.drop(["db_id"], axis=1)

    # apply some scaling to speed up the algorithm
    if SCALE_DATASET and scaler is None:
        x, scaler = perform_fit_scaling(x)
    elif SCALE_DATASET and scaler is not None:
        x = perform_scaling(x, scaler)

    log("Got %d instances with %d features for the dataset: %s." % (x.shape[0], x.shape[1], dataset))
    return x, y, ids, scaler
