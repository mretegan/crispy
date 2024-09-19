###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################

import functools
import logging
import time

logger = logging.getLogger(__name__)


def timeit(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        start = time.time()
        state = method(*args, **kwargs)
        stop = time.time()
        delta = stop - start
        message = f"{method}, {delta:.3g} seconds."
        logger.debug(message)
        return state

    return wrapper
