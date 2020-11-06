import json
from pathlib import Path
import os
import joblib
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


def store_onnx(path: str, pipeline, features):
    feature_names = ','.join(features)
    initial_type = [
        ('float_input', FloatTensorType([None, len(features)]))]
    onnx = convert_sklearn(
        pipeline, initial_types=initial_type, doc_string=feature_names)
    with open(path, 'wb') as f:
        f.write(onnx.SerializeToString())
    log(f'Stored onnx at: {path}')


def store_collection(collection, path):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(str(item) for item in collection))
    log(f"Stored collection at: {path}")
