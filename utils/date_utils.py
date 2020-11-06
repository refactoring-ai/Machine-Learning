from datetime import datetime


def now() -> str:
    return datetime.now().isoformat()


def windows_path_friendly_now() -> str:
    return now().replace(":", "-").replace(".", "-")
