import json
from statistics import mean
from pathlib import Path
import os
import joblib

from utils.log import log

# TODO: can we remove this function? format_results_single_run does the same
def format_results(dataset, refactoring_name, model_name, precision_scores, recall_scores,
                   accuracy_scores, tn, fp, fn, tp, best_model, features):
    results = "Production Model Results:"

    accuracy_scores_str = ', '.join(list([f"{e:.2f}" for e in accuracy_scores]))
    results += "\nAccuracy scores: " + accuracy_scores_str
    results += "\nMean Accuracy: %0.2f" % accuracy_scores.mean()

    precision_scores_str = ', '.join(list([f"{e:.2f}" for e in precision_scores]))
    results += "\nPrecision scores: " + precision_scores_str
    results += f'\nMean precision: {precision_scores.mean():.2f}'
    recall_scores_str = ', '.join(list([f"{e:.2f}" for e in recall_scores]))
    results += "\nRecall scores: " + recall_scores_str
    results += f'\nMean recall: {recall_scores.mean():.2f}\n'

    # summing up the results of the confusion matrix
    total_tn = sum(tn)
    total_fp = sum(fp)
    total_fn = sum(fn)
    total_tp = sum(tp)

    # TODO: print number by number of the confusion matrix
    # (for debugging purposes, we print it in the log already)

    # some models have the 'coef_' attribute, and others have the 'feature_importances_
    # (do not ask me why...)
    if hasattr(best_model, "coef_"):
        results += "\nFeatures:"
        results += (', '.join(str(e) for e in list(features)))
        results += "\nCoefficients:"
        results += "\n" + ''.join(str(e) for e in best_model.coef_.tolist())
    elif hasattr(best_model, "feature_importances_"):
        results += ("\nFeature Importances: \n" + ''.join(
            ["%-33s: %-5.4f\n" % (feature, importance) for feature, importance in
             zip(features, best_model.feature_importances_)]))
    else:
        results += "\n(Not possible to collect feature importances)"

    results += f'\nCSV,{dataset},{refactoring_name},{model_name},{precision_scores.mean():.2f},{recall_scores.mean():.2f},{accuracy_scores.mean()},{total_tn},{total_fp},{total_fn},{total_tp}'
    results += f'\nCSV2,{dataset},{refactoring_name},{model_name},precision,{precision_scores_str}'
    results += f'\nCSV2,{dataset},{refactoring_name},{model_name},recall,{recall_scores_str}'
    results += f'\nCSV2,{dataset},{refactoring_name},{model_name},accuracy,{accuracy_scores_str}'
    return results


# TODO: can we remove this function? format_results_single_run does the same
def format_test_results(dataset, refactoring_name, validation_names, model_name, precision_scores, recall_scores,
                        accuracy_scores, tn, fp, fn, tp) -> str:
    results = "Test Results for validation: " + str(validation_names)

    accuracy_scores_str = ', '.join(list([f"{e:.2f}" for e in accuracy_scores]))
    results += "\nAccuracy scores: " + accuracy_scores_str
    results += "\nMean Accuracy: %0.2f" % mean(accuracy_scores)

    precision_scores_str = ', '.join(list([f"{e:.2f}" for e in precision_scores]))
    results += "\nPrecision scores: " + precision_scores_str
    results += f'\nMean precision: {mean(precision_scores):.2f}'
    recall_scores_str = ', '.join(list([f"{e:.2f}" for e in recall_scores]))
    results += "\nRecall scores: " + recall_scores_str
    results += f'\nMean recall: {mean(recall_scores):.2f}\n'

    # summing up the results of the confusion matrix
    total_tn = sum(tn)
    total_fp = sum(fp)
    total_fn = sum(fn)
    total_tp = sum(tp)

    # TODO: print number by number of the confusion matrix
    # (for debugging purposes, we print it in the log already)

    results += f'\nCSV,{dataset},{refactoring_name},{model_name},{total_tn},{total_fp},{total_fn},{total_tp}'
    results += f'\nCSV2,{dataset},{refactoring_name},{model_name},precision,{precision_scores_str}'
    results += f'\nCSV2,{dataset},{refactoring_name},{model_name},recall,{recall_scores_str}'
    results += f'\nCSV2,{dataset},{refactoring_name},{model_name},accuracy,{accuracy_scores_str}'
    return results


def format_results_single_run(dataset, refactoring_name, validation_names, model_name, precision_scores, recall_scores,
                              accuracy_scores, tn, fp, fn, tp, best_model, features):
    """
    Format all specified scores and other relevant data  of the validation in a json format.
    """
    confusion_matrix = ""
    for index, validation_name in enumerate(validation_names):
        confusion_matrix += f"\nConfusion Matrix for validation set {validation_name}: " \
                            f"tn={tn[index]}, fp={fp[index]}, fn={fn[index]}, tp={tp[index]}"

    # some models have the 'coef_' attribute, and others have the 'feature_importances_
    # (do not ask me why...)
    coef_ = ""
    feature_importance = ""
    if hasattr(best_model, "coef_"):
        coef_ += "\nFeatures:"
        coef_ += (', '.join(str(e) for e in list(features)))
        coef_ += "\nCoefficients:"
        coef_ += "\n" + ''.join(str(e) for e in best_model.coef_.tolist())
    elif hasattr(best_model, "feature_importances_"):
        feature_importance += ("\nFeature Importances: \n" + ''.join(
            ["%-33s: %-5.4f\n" % (feature, importance) for feature, importance in
             zip(features, best_model.feature_importances_)]))
    else:
        coef_ += "\n(Not possible to collect feature importance)"
        feature_importance += "\n(Not possible to collect feature importance)"

    return json.dumps({"Model name": model_name,
                       "Refactoring type": refactoring_name,
                       "Training set": dataset,
                       "Validation sets": str(validation_names),
                       "Precision scores": ', '.join(list([f"{e:.2f}" for e in precision_scores])),
                       "Mean precision": f"{mean(precision_scores):.2f}",
                       "Recall scores": ', '.join(list([f"{e:.2f}" for e in recall_scores])),
                       "Mean recall": f"{mean(recall_scores):.2f}",
                       "Accuracy scores": ', '.join(list([f"{e:.2f}" for e in accuracy_scores])),
                       "Mean Accuracy": f"{mean(accuracy_scores):.2f}",
                       "Confusion matrix": confusion_matrix,
                       "coef_": coef_,
                       "feature_importance": feature_importance
                       }, indent=2, sort_keys=True)


def format_best_parameters(tuned_model):
    """
    Format the best parameters of the tuned model in a json format.
    """
    return json.dumps({"Hyperparametrization": json.dumps(tuned_model.best_params_, indent=2, sort_keys=True),
                       "Best_result": str(tuned_model.best_score_)}, indent=2, sort_keys=True)


def store_json(data, path: str):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True)
    log(f"Stored json at: {path}")


def store_joblib(data, path):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        joblib.dump(data, path)
    log(f"Stored joblib at: {path}")


def store_collection(collection, path):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(str(item) for item in collection))
    log(f"Stored collection at: {path}")