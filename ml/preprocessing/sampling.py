import pandas as pd
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler, ClusterCentroids, NearMiss
from configs import BALANCE_DATASET_STRATEGY, CORE_COUNT
from utils.log import log


def sample_reduction(dataset, fraction):
    """
    Reduce the number of samples in the dataset to the given fraction.

    Parameter:
    dataset
        The data frame to reduce
    fraction
        Fraction of the initial samples [0 - 1]
    """
    initial_count = len(dataset.index)
    dataset = dataset.sample(frac=fraction)
    log(f"Reduced number of samples from {initial_count} to {len(dataset.index)} ({fraction})", False)
    return dataset


def perform_balancing(x, y, strategy=None):
    """
    Performs under/over sampling, according to the number of true and false instances of the x, y dataset.
    :param x: feature values
    :param y: labels
    :return: a balanced x, y
    """

    if strategy is None:
        strategy = BALANCE_DATASET_STRATEGY

    if strategy == 'random':
        # more info: https://imbalanced-learn.readthedocs.io/en/stable/under_sampling.html
        rus = RandomUnderSampler(random_state=42)  # 42 is a random number, just to ensure our results are reproducible
    elif strategy == 'oversampling':
        rus = RandomOverSampler(random_state=42)
    elif strategy == 'cluster_centroids':
        rus = ClusterCentroids(random_state=42, n_jobs=CORE_COUNT)
    elif strategy == 'nearmiss':
        rus = NearMiss(version=1, n_jobs=CORE_COUNT)
    else:
        raise Exception("algorithm not found")

    # keeping column names
    new_x, new_y = rus.fit_resample(x, y)
    new_x = pd.DataFrame(new_x, columns=x.columns)
    return new_x, new_y
