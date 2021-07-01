#!/usr/bin/env python3
# coding: utf-8
###################################################################
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################

import unittest
from crispy.quanty.tests.test_quanty import suite as test_quanty_suite


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(test_quanty_suite())
    return test_suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(failfast=False)
    runner.run(suite())
