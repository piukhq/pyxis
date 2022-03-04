from dataclasses import dataclass


class Table:
    def __init__(self, table_scheme, data):
        self.data = data
        self.table_scheme = table_scheme

    @property
    def values_as_list(self):
        return list(self.table_scheme.__dict__.values())

    def keys_as_list(self):
        return list(self.__dict__.keys())


def id_generator(starting_num: int = 0):
    num = starting_num
    while True:
        yield num
        num += 1