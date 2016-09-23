from functools import wraps
from contextlib import contextmanager

import time


def timefunc(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.clock()
        r = func(*args, **kwargs)
        end = time.clock()
        print '{}.{}: {} seconds'.format(func.__module__, func.__name__, end-start)
        return r
    return wrapper


@contextmanager
def timeblock(label):
    start = time.clock()
    try:
        yield
    finally:
        end = time.clock()
        print '{} : {}'.format(label, end-start)

