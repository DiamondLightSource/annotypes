import inspect
from collections import OrderedDict

from ._make import make_repr, make_call_types
from ._anno import Anno
from .typing import Dict


class CallTypesMeta(type):
    def __init__(cls, name, bases, dct):
        f = dct.get('__init__', None)
        if f:
            frame = inspect.currentframe(1)
            cls.call_types = make_call_types(f, frame.f_locals)
        super(CallTypesMeta, cls).__init__(name, bases, dct)


class WithCallTypes(object):
    call_types = None  # type: Dict[str, Anno]

    __metaclass__ = CallTypesMeta

    def __repr__(self):
        repr_str = make_repr(self, self.call_types)
        return repr_str


def to_dict(inst):
    # type: (WithCallTypes) -> OrderedDict
    ret = OrderedDict()
    for k in inst.call_types:
        ret[k] = getattr(inst, k)
    return ret


def add_call_types(f):
    frame = inspect.currentframe(1)
    f.call_types = make_call_types(f, frame.f_locals)
    return f
