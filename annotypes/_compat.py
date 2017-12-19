import inspect
import sys


# Taken from six
def add_metaclass(metaclass):
    """Class decorator for creating a class with a metaclass."""
    def wrapper(cls):
        orig_vars = cls.__dict__.copy()
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)
        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper


def getargspec(f):
    if sys.version_info < (3,):
        return inspect.getargspec(f)
    else:
        return inspect.getfullargspec(f)
