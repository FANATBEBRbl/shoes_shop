"""Bundled resources and editable settings have different base directories."""
from pathlib import Path
import sys


def resource_path(relative):
    return Path(__file__).resolve().parent / relative


def external_config_path():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "config.ini"
    return Path(__file__).resolve().parent / "config.ini"
