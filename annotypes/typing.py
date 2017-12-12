# Import the things we need from typing if it exists
try:
    from typing import (
        TYPE_CHECKING, TypeVar, Any, overload,
        # Things that take parameters
        Generic, Sequence, List, Dict, Optional, Callable, Union,
    )
except ImportError:
    # A minimal set of the objects we need for runtime compatibility with typing
    TYPE_CHECKING = False

    class TypeVar(object):
        def __init__(self, name, *constraints, **kwargs):
            pass

    class Any(object):
        pass

    def overload(f):
        def bad(*args, **kwargs):
            raise NotImplementedError()
        return bad

    class _Gettable(type):
        def __getitem__(self, params):
            return self.__class__(self.__name__)

    class Generic(object):
        __metaclass__ = _Gettable

    class Sequence(Generic):
        pass

    class List(Generic):
        pass

    class Dict(Generic):
        pass

    class Optional(object):
        __metaclass__ = _Gettable

    class Callable(object):
        __metaclass__ = _Gettable

    class Union(object):
        __metaclass__ = _Gettable


