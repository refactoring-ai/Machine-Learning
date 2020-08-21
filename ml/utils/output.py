import json
from pathlib import Path
import os
import joblib
from utils.log import log


def format_results_single_run(dataset, refactoring_name, validation_names, model_name, precision_scores, recall_scores,
                              accuracy_scores, tn, fp, fn, tp, permutation_importances, best_model, features):
    """
    Format all specified scores and other relevant data  of the validation in a json format.
    """
    confusion_matrix = ""
    permutation_importances_dict = {}
    for index, validation_name in enumerate(validation_names):
        confusion_matrix += f"\n{validation_name}: tn={tn[index]}, fp={fp[index]}, fn={fn[index]}, tp={tp[index]}"
        permutation_importance = permutation_importances[index]
        permutation_importances_dict[validation_name] = {feature: (mean, std) for feature, mean, std in zip(features, permutation_importance.importances_mean, permutation_importance.importances_std)}

    # some models have the 'coef_' attribute, and others have the 'feature_importances_
    # (do not ask me why...)
    coefficients = {}
    feature_importances = {}
    if hasattr(best_model, "coef_"):
        coefficients = {feature: coef for feature, coef in zip(features, best_model.coef_.tolist())}
    elif hasattr(best_model, "feature_importances_"):
        feature_importances = {feature: importance for feature, importance in zip(features, best_model.feature_importances_)}

    return json.dumps({"model_name": model_name,
                       "refactoring type": refactoring_name,
                       "training_set": dataset,
                       "validation_sets": str(validation_names),
                       "precision_scores": ', '.join(list([f"{e:.2f}" for e in precision_scores])),
                       "mean_precision": f"{mean(precision_scores):.2f}",
                       "recall_scores": ', '.join(list([f"{e:.2f}" for e in recall_scores])),
                       "mean_recall": f"{mean(recall_scores):.2f}",
                       "accuracy_scores": ', '.join(list([f"{e:.2f}" for e in accuracy_scores])),
                       "mean_accuracy": f"{mean(accuracy_scores):.2f}",
                       "confusion_matrix": confusion_matrix,
                       "feature_coefficients": json.dumps(coefficients, indent=2, sort_keys=True),
                       "feature_importance":  json.dumps(feature_importances, indent=2, sort_keys=True),
                       "permutation_importance":  json.dumps(permutation_importances_dict, indent=2, sort_keys=True)
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
