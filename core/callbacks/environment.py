import tomllib
from pathlib import Path

from django.conf import settings


def _get_project_version():
    with Path("pyproject.toml").open("rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def callback(_):
    version = _get_project_version()
    return [version, "success" if not settings.DEBUG else "warning"]
