from collections import OrderedDict

from ._make import make_repr, make_call_types
from ._anno import Anno, caller_locals
from ._type_checking import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict


# Taken from six
def add_metaclass(metaclass):
    """Class decorator for creating a class with a metaclass."""
    def wrapper(cls):
        orig_vars = cls.__dict__.copy()
        slots = orig_vars.get('__slots__')
        if slots is not None:
            if isinstance(slots, str):
                slots = [slots]
            for slots_var in slots:
                orig_vars.pop(slots_var)
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)
        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper


class CallTypesMeta(type):
    def __init__(cls, name, bases, dct):
        f = dct.get('__init__', None)
        if f:
            cls.call_types = make_call_types(f, caller_locals())
        super(CallTypesMeta, cls).__init__(name, bases, dct)


@add_metaclass(CallTypesMeta)
class WithCallTypes(object):
    call_types = None  # type: Dict[str, Anno]

    def __repr__(self):
        repr_str = make_repr(self, self.call_types)
        return repr_str


def to_dict(inst):
    # type: (WithCallTypes) -> OrderedDict
    ret = OrderedDict()  # type: OrderedDict
    for k in inst.call_types:
        value = getattr(inst, k)
        if hasattr(value, "name"):
            ret[k] = value.name
        else:
            ret[k] = value
    return ret


def add_call_types(f):
    f.call_types = make_call_types(f, caller_locals())
    return f
