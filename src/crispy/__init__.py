###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""This is the Crispy package."""

__version__ = "0.8.0"
import os
import sys

version = __version__


# https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
def resourceAbsolutePath(relativePath):
    """Get the absolute path to a resource. Works for development and for PyInstaller."""
    basePath = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(basePath, relativePath)
