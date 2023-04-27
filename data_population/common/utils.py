import logging
import random
import string
import time

from typing import Any, Callable, Generator


def id_generator(starting_num: int = 0) -> Generator[int, None, None]:
    """Python generator used by table-data generators to produce sequential ids."""
    num = starting_num
    while True:
        yield num
        num += 1


def timed_function(func: Callable) -> Callable:
    """Times functions...!"""

    def inner(*args: Any, **kwargs: Any) -> None:
        logger = logging.getLogger("FunctionTimer")

        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()

        logger.debug(f"Function [{func.__name__}] completed in {end_time-start_time} seconds")

    return inner


def random_ascii(length: int = 10) -> str:
    """Generate a random ascii string of n length"""
    return "".join(random.choice(string.ascii_lowercase) for i in range(length))
