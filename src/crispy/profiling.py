
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
