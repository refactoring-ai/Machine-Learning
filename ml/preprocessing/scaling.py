import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def perform_fit_scaling(x):
    """
    Scales all the values between [0,1]. It often speeds up the learning process.

    :param x: the feature values
    :return: x, scaled
    """
    scaler = MinMaxScaler()  # Default behavior is to scale to [0,1]
    x = scaler.fit_transform(x)
    x = pd.DataFrame(x, columns=x.columns, index=x.index)

    return x, scaler


def perform_scaling(x, scaler):
    """
    Scales all the values between [0,1]. It often speeds up the learning process.

    :param x: the feature values
    :param scaler: a predefined and fitted scaler, e.g. a MinMaxScaler
    :return: x, scaled
    """
    x = scaler.transform(x)
    x = pd.DataFrame(x, columns=x.columns, index=x.index)

    return x
