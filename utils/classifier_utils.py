import csv
import json
from pathlib import Path
import os
from typing import Iterable
import joblib
from sklearn.pipeline import Pipeline
from uuid import uuid4
from utils.log import log
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from configs import JOBLIB_COMPRESSION


def format_best_parameters(tuned_model):
    """
    Format the best parameters of the tuned model in a json format.
    """
    return {"Hyperparametrization": tuned_model.best_params_,
            "Best_result": str(tuned_model.best_score_)}


def store_json(data, path: str):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    log(f"Stored json at: {path}")


def store_joblib(data, path):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    joblib.dump(data, path, compress=JOBLIB_COMPRESSION)
    log(f"Stored joblib at: {path}")


def store_onnx(path: str, pipeline: Pipeline, model_type: str, feature_names: Iterable[str], refactoring_type: str, trained_on):
    doc = {"id": str(uuid4()), "model_type": model_type, "refactoring_type": refactoring_type, "trained_on": trained_on,
           "feature_names": feature_names.tolist()}

    initial_type = [
        ('float_input', FloatTensorType([None, len(feature_names)]))]
    onnx = convert_sklearn(
        pipeline, initial_types=initial_type, doc_string=json.dumps(doc))
    with open(path, 'wb') as f:
        f.write(onnx.SerializeToString())
    log(f'Stored onnx at: {path}')


def store_collection(collection, path):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(str(item) for item in collection))
    log(f"Stored collection at: {path}")


def load_joblib(path):
    return joblib.load(path)


def load_csv(path):
    with open(path) as file:
        reader = csv.reader(file)
        data_raw = list(reader)
        return [item for sublist in data_raw for item in sublist]
