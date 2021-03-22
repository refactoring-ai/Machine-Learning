import json
from os import path
from utils import date_utils
from pathlib import Path
import configs

_f = None


def log_config():
    global _f

    # create a dict of the entire config class, to capture all fields
    config_dict = configs.__dict__
    # filter to get only the public fields that we created
    config_dict = {k: v for k, v in config_dict.items() if k.isupper()}
    # log the config with some nice json formatting, but hide it from the
    # terminal
    # log_msg = json.dumps(config_dict, indent=2, sort_keys=True)
    log(f"--------------\nConfiguration:\n{config_dict}\n--------------")


def log_init(log_name: str = ""):
    global _f
    if len(log_name) > 0:
        Path(path.dirname(log_name)).mkdir(parents=True, exist_ok=True)
        _f = open(log_name, "w+")
    else:
        dir_path = path.join(configs.RESULTS_DIR_PATH, "results")
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        _f = open(
            path.join(
                dir_path,
                f"{date_utils.windows_path_friendly_now()}.log"),
            "w+")


def log_close():
    global _f
    _f.close()


def log(msg):
    if not isinstance(msg, str):
        msg = json.dumps(msg, indent=2)
    print(msg)
    global _f
    _f.write(msg)
    _f.write("\n")
    _f.flush()
