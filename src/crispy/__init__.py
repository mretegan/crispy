"""This is the Crispy package."""

__version__ = "0.8.0"
import os
import sys

version = __version__


# https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
def resourceAbsolutePath(relativePath):
    """Get the absolute path to a resource."""
    basePath = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(basePath, relativePath)
