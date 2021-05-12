from itertools import count, islice
from random import randint


def isfloat(v):
    try:
        float(v)
    except ValueError:
        return False
    except TypeError:
        return False
    return True


def isint(v):
    try:
        int(v)
    except ValueError:
        return False
    except TypeError:
        return False
    return True


def create_int_list(start_num, end_num=None):
    if end_num is not None:
        return [el for el in islice(count(start_num), end_num + 1)]
    else:
        return [el for el in islice(count(start_num), randint(1, abs(start_num) + 20))]


global f_path
f_path = 'C:\\PyProjects\\parsing-data\\files\\'
