from functools import wraps
import time


def timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.clock()
        r = func(*args, **kwargs)
        end = time.clock()
        print '{}.{}:{}'.format(func.__module, func.__name__, end-start)
        return r
    return wrapper
