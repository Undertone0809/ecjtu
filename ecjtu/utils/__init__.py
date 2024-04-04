import os
import tempfile
from datetime import datetime, timedelta


def convert_backslashes(path: str):
    """Convert all \\ to / of file path."""
    return path.replace("\\", "/")


def get_default_storage_path(module_name: str = "") -> str:
    storage_path = os.path.expanduser("~/.ecjtu")

    if module_name:
        storage_path = os.path.join(storage_path, module_name)

    # Try to create the storage path (with module subdirectory if specified)
    # Use a temporary directory instead if permission is denied,
    try:
        os.makedirs(storage_path, exist_ok=True)
    except PermissionError:
        storage_path = os.path.join(tempfile.gettempdir(), "ecjtu", module_name)
        os.makedirs(storage_path, exist_ok=True)

    return convert_backslashes(storage_path)


def get_today_date() -> str:
    """Get today's date in the format of "YYYY-MM-DD".

    Returns:
        str: Today's date
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_cur_week_datetime() -> datetime:
    """Get the start datetime of the current week."""
    today = datetime.now()
    return today - timedelta(days=today.weekday())


def get_cur_semester() -> str:
    """Get the current semester, eg: 2023.1 or 2022.2

    Returns:
        str: The current semester
    """
    now = datetime.now()
    if now.month < 9:
        return f"{now.year - 1}.2"
    return f"{now.year}.1"


def get_last_semester() -> str:
    """Get the last semester, eg: 2023.1 or 2022.2

    Returns:
        str: The last semester
    """
    now = datetime.now()
    if now.month < 9:
        return f"{now.year - 1}.1"
    return f"{now.year}.2"
