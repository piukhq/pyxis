from enum import Enum


def id_generator(starting_num: int = 0):
    num = starting_num
    while True:
        yield num
        num += 1