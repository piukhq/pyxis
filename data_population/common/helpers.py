def id_generator(starting_num: int = 0):
    """
    Python generator used by table-data generators to produce sequential ids.
    """
    num = starting_num
    while True:
        yield num
        num += 1
