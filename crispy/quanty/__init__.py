###################################################################
# Copyright (c) 2016-2022 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""This package provides functionality related to Quanty calculations."""

import os

import xraydb
import yaml

from crispy import resourceAbsolutePath

XDB = xraydb.XrayDB()

path = os.path.join("quanty", "calculations.yaml")
with open(resourceAbsolutePath(path), encoding="utf-8") as fp:
    CALCULATIONS = yaml.load(fp, Loader=yaml.FullLoader)
