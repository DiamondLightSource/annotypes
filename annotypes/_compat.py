import inspect
import sys

from ._typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable


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
        args, varargs, keywords, defaults = inspect.getargspec(f)
    else:
        # Need to use fullargspec in case there are annotations
        args, varargs, keywords, defaults = inspect.getfullargspec(f)[:4]
    return inspect.ArgSpec(args, varargs, keywords, defaults)


def func_globals(f):
    if sys.version_info < (3,):
        return f.func_globals
    else:
        return f.__globals__
