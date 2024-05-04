"""
Utils Module
"""

from pathlib import Path


def mkdir(path: Path, parents: bool = True):
    try:
        path.mkdir(parents=parents)
    except FileExistsError:
        pass
