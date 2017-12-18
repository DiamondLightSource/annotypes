from collections import OrderedDict
import copy

from ._make import make_repr, make_annotations, getargspec
from ._anno import Anno, caller_locals_globals, NO_DEFAULT
from ._type_checking import TYPE_CHECKING

from typing import Union

if TYPE_CHECKING:
    from typing import Dict, Callable, Any, Tuple


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
            cls.call_types, _ = make_call_types(f, *caller_locals_globals())
        else:
            cls.call_types = OrderedDict()
        anno = Anno("Class instance")
        anno.typ = cls
        cls.return_type = anno
        super(CallTypesMeta, cls).__init__(name, bases, dct)


@add_metaclass(CallTypesMeta)
class WithCallTypes(object):
    call_types = None  # type: Dict[str, Anno]
    return_type = None  # type: Anno

    def __repr__(self):
        repr_str = make_repr(self, self.call_types)
        return repr_str


def to_dict(inst):
    # type: (WithCallTypes) -> OrderedDict
    ret = OrderedDict()  # type: OrderedDict
    for k in inst.call_types:
        ret[k] = getattr(inst, k)
    return ret


def add_call_types(f):
    f.call_types, f.return_type = make_call_types(f, *caller_locals_globals())
    return f


# A sentinel meaning we were called with no default as it is a return value
RETURN_DEFAULT = object()


def anno_with_default(anno, default=RETURN_DEFAULT):
    if getattr(anno, "__origin__", None) == Union:
        # if any of the types are NoneType then it is optional
        optional = type(None) in anno.__args__
        # the anno is actually the first parameter to Optional or Union
        anno = anno.__args__[0]  # type: Anno
        assert isinstance(anno, Anno), \
            "Expected Optional[Anno], Union[Anno,...] or Anno, got %r" % (anno,)
        # if this is a return type and optional, default should be None
        if optional:
            if default is RETURN_DEFAULT:
                default = None
            assert default is None, \
                "Expected Optional[Anno] with default=None, got %r with " \
                "default=%r" % (anno, default)
    # Make a copy of the anno with the new default if needed
    if default not in (RETURN_DEFAULT, NO_DEFAULT):
        anno = copy.copy(anno)
        anno.default = default
    return anno


def make_call_types(f, locals_d, globals_d):
    # type: (Callable, Dict, Dict) -> Tuple[Dict[str, Anno], Anno]
    """Make a call_types dictionary that describes what arguments to pass to f

    Args:
        f: The function to inspect for argument names (without self)
        locals_d: A dictionary of locals to lookup annotation definitions in
        globals_d: A dictionary of globals to lookup annotation definitions in
    """
    arg_spec = getargspec(f)
    args = [k for k in arg_spec.args if k != "self"]

    defaults = {}  # type: Dict[str, Any]
    if arg_spec.defaults:
        default_args = args[-len(arg_spec.defaults):]
        for a, default in zip(default_args, arg_spec.defaults):
            defaults[a] = default

    if not getattr(f, "__annotations__", None):
        # Make string annotations from the type comment if there is one
        annotations = make_annotations(f, locals_d, globals_d)
    else:
        annotations = f.__annotations__

    call_types = OrderedDict()  # type: Dict[str, Anno]
    for a in args:
        anno = anno_with_default(annotations[a], defaults.get(a, NO_DEFAULT))
        assert isinstance(anno, Anno), \
            "Argument %r has type %r which is not an Anno" % (a, anno)
        call_types[a] = anno

    return_type = anno_with_default(annotations["return"])
    assert return_type is None or isinstance(return_type, Anno), \
        "Return has type %r which is not an Anno" % (return_type,)

    return call_types, return_type
