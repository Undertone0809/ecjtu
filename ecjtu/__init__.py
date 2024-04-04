# type: ignore[attr-defined]
"""ECJTU API SDK service"""

import sys

from ecjtu.client import ECJTU, AsyncECJTU
from ecjtu.models import GPA, ElectiveCourse, ScheduledCourse, Score

if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()
__all__ = ["ECJTU", "AsyncECJTU", "GPA", "ElectiveCourse", "ScheduledCourse", "Score"]
