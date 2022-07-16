"""Utilities shared among multiple files.

AUTHOR: Matteo Paltenghi
"""
import yaml
import pathlib

def read_yaml_file(filename):
    """Reads a yaml file and returns a dictionary."""
    with open(filename, "r") as f:
        return yaml.safe_load(f)


def get_root_directory():
    """Returns the root directory of the project."""
    return pathlib.Path(__file__).parent.resolve()