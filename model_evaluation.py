import glob
import json
import os.path
import pandas as pd
from configs import Level
from ml.preprocessing.preprocessing import retrieve_labelled_instances
from ml.refactoring import build_refactorings
from utils.classifier_utils import load_joblib, evaluate_model, format_results_single_run, load_csv, store_json
from utils.log import log_init, log, log_close
import datetime

MODEL_DIRECTORY = "results/reproduction/model/"
SCALER_DIRECTORY = "results/reproduction/scaler/"
SAVE_DIRECTORY = "results/Evaluations/reproduction/"
DATASET = "github"


def find_path(pattern, file_extension, directory):
    matches = glob.glob(f"{directory}{pattern}*.{file_extension}")
    if len(matches) > 0:
        return matches[0]
    return None


def get_model(refactoring_name, model_name):
    model_lookup = f"model_{model_name}_{DATASET}_{refactoring_name.replace(' ', '')}"
    modelPath = find_path(model_lookup, "joblib", MODEL_DIRECTORY)
    scaler_lookup = f"scaler_{model_name}_{DATASET}_{refactoring_name.replace(' ', '')}"
    scalerPath = find_path(scaler_lookup, "joblib", SCALER_DIRECTORY)
    features_lookup = f"features_{model_name}_{DATASET}_{refactoring_name.replace(' ', '')}"
    featuresPath = find_path(features_lookup, "csv", MODEL_DIRECTORY)

    if modelPath is not None:
        trained_model = load_joblib(modelPath)
        features = load_csv(featuresPath)
        model_scaler = load_joblib(scalerPath)
        return trained_model, model_scaler, features
    else:
        return None, None, None


def save_validation_results(model_name, test_result, test_name, formatted_results):
    results_path = f"{SAVE_DIRECTORY}/predictions/predictions_{model_name}_{DATASET}_{test_name}_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
    data = {
        'test_scores': formatted_results,
        'test_results': test_result.to_json()
    }
    store_json(data, results_path)


def process_model(refactoring, model_name, trained_model, model_scaler, features):
    # Train and val the model
    x_val, y_val, db_ids_val, _, = retrieve_labelled_instances("test set github", refactoring, False, model_scaler)

    drop_list = [column for column in x_val.columns.values if column not in features]
    x_val = x_val.drop(drop_list, axis=1)
    assert x_val.shape[1] == len(features), "Incorrect number of features!"
    log(f"Reduced the feature count to {len(features)}.")

    # evaluate the model
    val_scores, val_results = evaluate_model(trained_model, [x_val], [y_val], [db_ids_val])
    formatted_results = format_results_single_run(DATASET, refactoring_name, ["test set github"], model_name, val_scores["f1_score"],
                                                  val_scores["precision"],
                                                  val_scores["recall"], val_scores['accuracy'], val_scores['tn'],
                                                  val_scores['fp'], val_scores['fn'], val_scores['tp'],
                                                  val_scores["permutation_importance"],
                                                  trained_model, features, json.dumps(trained_model.get_params()))
    save_validation_results(model_name, val_results[0], "test set github", formatted_results)
    return formatted_results, trained_model.get_params()


# Start
log_init(f"{SAVE_DIRECTORY}classifier_evaluation_test-set_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt")
log('Begin classifier evaluation')

refactorings = build_refactorings(Level)

for model_name in ["LogisticRegressionRefactoringModel", "RandomForestRefactoringModel"]:
    evaluation_path = f"{SAVE_DIRECTORY}test_set_evaluation{model_name}.xlsx"
    params_path = f"{SAVE_DIRECTORY}{model_name}_parameter.xlsx"
    if not os.path.exists(evaluation_path):
        evaluation_results = pd.DataFrame()
        parameter_sets = pd.DataFrame()
        for refactoring in refactorings:
            refactoring_name = refactoring.name()
            trained_model, model_scaler, features = get_model(refactoring_name, model_name)

            if trained_model is not None:
                formatted_results, params = process_model(refactoring, model_name, trained_model, model_scaler, features)
                log(formatted_results)
                params["model_name"] = model_name
                params["refactoring"] = refactoring_name
                parameter_sets = parameter_sets.append(params, ignore_index=True)
                evaluation_results = evaluation_results.append(json.loads(formatted_results), ignore_index=True)
        evaluation_results.to_excel(evaluation_path)
        parameter_sets.to_excel(params_path)
    else:
        log(f"Skipped evaluation for {model_name} because it was already done.")
log_close()
exit()
