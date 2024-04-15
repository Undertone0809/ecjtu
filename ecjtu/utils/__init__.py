from datetime import datetime, timedelta


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
