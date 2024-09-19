###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""This package provides functionality related to Quanty calculations."""

import os

import xraydb
from ruamel.yaml import YAML

from crispy import resourceAbsolutePath

XDB = xraydb.XrayDB()

path = os.path.join("quanty", "calculations.yaml")
with open(resourceAbsolutePath(path), encoding="utf-8") as fp:
    yaml = YAML(pure=True)
    CALCULATIONS = yaml.load(fp)
