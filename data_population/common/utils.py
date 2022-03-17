import logging
import random
import string
import time

from typing import Iterable


def id_generator(starting_num: int = 0) -> Iterable[int]:
    """Python generator used by table-data generators to produce sequential ids."""
    num = starting_num
    while True:
        yield num
        num += 1


def timed_function(func):  # type: ignore
    """Times functions...!"""

    def inner(*args, **kwargs):  # type: ignore

        logger = logging.getLogger("FunctionTimer")

        t = time.time()
        func(*args, **kwargs)
        n = time.time()

        logger.debug(f"Function [{func.__name__}] completed in {n-t} seconds")

    return inner


def random_ascii(length: int = 10) -> str:
    """Generate a random ascii string of n length"""
    return "".join(random.choice(string.ascii_lowercase) for i in range(length))
