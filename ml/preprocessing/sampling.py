import pandas as pd
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler, ClusterCentroids, NearMiss
from configs import BALANCE_DATASET_STRATEGY, CORE_COUNT, SEED
from utils.log import log


def sample_reduction(positive_samples, negative_samples, ratio: float):
    """
    Reduce the number of training samples in the dataset to the match the given ratio
    Parameter:
        positive_samples (DataFrame):    The positive training samples
        negative_samples (DataFrame):   The negative training samples
        ratio  (float):                 Ratio of the positive and negative samples for the training, e.g. 0.1 -> 10/% positive samples
    """
    # apply the lower boundary to the fraction, ensure the fraction is still
    # in range 0 - 1
    total_count = len(positive_samples.index) + len(negative_samples.index)
    fraction_positive = total_count * ratio / len(positive_samples.index)
    fraction_negative = total_count * (1 - ratio) / len(negative_samples.index)
    # positive limits
    if fraction_positive > 1.0:
        fraction_negative = len(positive_samples.index) * \
            ((1 - ratio) / ratio) / len(negative_samples.index)
        fraction_positive = 1.0
    # negative limits
    elif fraction_negative > 1.0:
        fraction_positive = len(negative_samples.index) * \
            (ratio / (1 - ratio)) / len(positive_samples.index)
        fraction_negative = 1.0

    positive_samples = positive_samples.sample(frac=fraction_positive)
    negative_samples = negative_samples.sample(frac=fraction_negative)
    log(
        f"Reduced the number of samples to {len(positive_samples.index)}/ {len(negative_samples.index)} ({ratio}/ {1-ratio})",
        False)
    return positive_samples, negative_samples


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
        # more info:
        # https://imbalanced-learn.readthedocs.io/en/stable/under_sampling.html
        rus = RandomUnderSampler(random_state=SEED)
    elif strategy == 'oversampling':
        rus = RandomOverSampler(random_state=SEED)
    elif strategy == 'cluster_centroids':
        rus = ClusterCentroids(random_state=SEED, n_jobs=CORE_COUNT)
    elif strategy == 'nearmiss':
        rus = NearMiss(version=1, n_jobs=CORE_COUNT)
    else:
        raise ValueError("algorithm not found")

    # keeping column names
    new_x, new_y = rus.fit_resample(x, y)
    new_x = pd.DataFrame(new_x, columns=x.columns)
    return new_x, new_y
