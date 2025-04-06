"""Utilities shared among multiple files.

AUTHOR: Matteo Paltenghi
"""
import yaml
import pathlib
import os
import platform
import subprocess


def read_yaml_file(filename):
    """Reads a yaml file and returns a dictionary."""
    with open(filename, "r") as f:
        return yaml.safe_load(f)


def get_root_directory():
    """Returns the root directory of the project."""
    return pathlib.Path(__file__).parent.resolve()


def get_host_address():
    """Get the appropriate host address based on the platform."""
    if platform.system() == "Windows":
        return "127.0.0.1"
    else:
        # Assume Linux/Unix/Mac for everything else
        return "0.0.0.0"
