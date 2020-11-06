import json
from os import path
import random
from pathlib import Path
import configs

_f = None


def log_config():
    global _f

    # create a dict of the entire config class, to capture all fields
    config_dict = configs.__dict__
    # filter to get only the public fields that we created
    config_dict = {k: v for k, v in config_dict.items() if k.isupper()}
    # log the config with some nice json formatting, but hide it from the terminal
    log_msg = json.dumps(config_dict, indent=2, sort_keys=True), False
    log(f"--------------\nConfiguration:\n{log_msg}\n--------------", False)


def log_init(log_name: str = ""):
    global _f
    if len(log_name) > 0:
        Path(path.dirname(log_name)).mkdir(parents=True, exist_ok=True)
        _f = open(log_name, "w+")
    else:
        dir_path = path.join(configs.RESULTS_DIR_PATH, "results")
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        _f = open(
            path.join(dir_path, f"{random.randint(1, 999999)}-result.txt"), "w+")

    log(r"  __  __ _      _ _    ___      __         _           _           ")
    log(r" |  \/  | |    | | |  | _ \___ / _|__ _ __| |_ ___ _ _(_)_ _  __ _ ")
    log(r" | |\/| | |__  |_  _| |   / -_)  _/ _` / _|  _/ _ \ '_| | ' \/ _` |")
    log(r" |_|  |_|____|   |_|  |_|_\___|_| \__,_\__|\__\___/_| |_|_||_\__, |")
    log(r"                                                             |___/ ")
    log("")

    log_config()


def log_close():
    global _f
    _f.close()


def log(msg, print_msg: bool = True):
    if not isinstance(msg, str):
        msg = json.dumps(msg, indent=2)
    if print_msg:
        print(msg)
    global _f
    _f.write(msg)
    _f.write("\n")
    _f.flush()
