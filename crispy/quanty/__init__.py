# coding: utf-8
###################################################################
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""This package provides functionality related to Quanty calculations."""

import os
import json
import xraydb

from crispy import resourceAbsolutePath

XDB = xraydb.XrayDB()

path = os.path.join("quanty", "calculations.json")
with open(resourceAbsolutePath(path), encoding="utf-8") as fp:
    CALCULATIONS = json.load(fp, object_hook=dict)
