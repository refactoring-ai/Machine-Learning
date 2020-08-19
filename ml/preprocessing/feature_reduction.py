from sklearn.feature_selection import RFECV
from sklearn.svm import SVR
from configs import N_CV_FEATURE_REDUCTION
from utils.log import log


def feature_selection_rfecv(estimator, X, y):
    """
    Performs feature reduction on X with y labels for the given estimator with RFE-CV.

    :param estimator: RFE trains this estimator with the features, and recursively removes them
    :param X: feature values
    :param y: labels

    :return: x, where x only contains the relevant features.
    """
    selector = RFECV(estimator, step=1, cv=N_CV_FEATURE_REDUCTION, n_jobs=-1)

    selector.fit(X, y)
    log(f"Feature ranking: {', '.join(str(e) for e in selector.ranking_)}", False)
    log(f"Feature grid scores: {', '.join(str(e) for e in selector.grid_scores_)}", False)
    return X[X.columns[selector.get_support(indices=True)]] # keeping the column names


def perform_feature_reduction(estimator, X, y, allowed_features=None):
    """
    Reduce the features of X for the estimator, or reduce the features to the given list of features.

    :param :
        estimator: RFE trains this estimator with the features, and recursively removes them
        X: feature values
        y: labels
        allowed_features: reduce the features to this list

    :return :
        features: an array with the features of the instances
        X: X, with only potentially relevant features
    """
    log(f"Features before reduction (total of {len(X.columns.values)}): {', '.join(X.columns.values)}", False)
    # let's reduce the number of features in the set
    if allowed_features is None:
        # not all estimators expose coef_ or feature_importances, thus we handle these cases with a default estimator
        try:
            X = feature_selection_rfecv(estimator, X, y)
        except(RuntimeError):
            log(f"The classifier does not expose coef_ or feature_importances_, thus we use an SVR estimator as a replacement for feature reduction.", False)
            X = feature_selection_rfecv(SVR(kernel="linear"), X, y)

    # enforce the specified feature set
    elif allowed_features is not None:
        drop_list = [column for column in X.columns.values if column not in allowed_features]
        X = X.drop(drop_list, axis=1)
        assert X.shape[1] == len(allowed_features), "Incorrect number of features!"

    log(f"Features after reduction (total of {len(X.columns.values)}): {', '.join(X.columns.values)}")
    return X.columns.values, X
