import re
import tokenize
import inspect
from collections import OrderedDict

from .typing import Sequence, Any, Callable, Dict


type_re = re.compile('^# type: ([^-]*)( -> (.*))?$')


def make_annotations(f, locals_d):
    """Create an annotations dictionary from Python2 type comments

    http://mypy.readthedocs.io/en/latest/python2.html

    Args:
        f: The function to examine for type comments
        locals_d: The locals dictionary to get type idents from
    """
    # type: (Callable, Dict) -> Dict[str, type]
    lines, _ = inspect.getsourcelines(f)
    arg_spec = inspect.getargspec(f)
    args = [k for k in arg_spec.args if k != "self"]
    it = iter(lines)
    ret = {}
    for a in args:
        ret[a] = Any
    names = []
    for token in tokenize.generate_tokens(lambda: next(it)):
        typ, string, start, end, line = token
        if typ == tokenize.COMMENT:
            found = type_re.match(string)
            if found:
                parts = found.groups()
                if parts[0] == "(...)":
                    # Can't eval this in python2
                    types = Ellipsis
                else:
                    types = eval(parts[0], locals_d, locals())
                if isinstance(types, tuple):
                    # We got more than one argument, so add type comments
                    # to all args of the functions
                    ret.update(zip(args, types))
                elif types != Ellipsis:
                    # We got a single argument, so just type the first ident
                    # on the line
                    ret[names[0]] = types
                names = []
        elif typ == tokenize.NAME:
            names.append(string)
    return ret


def make_repr(inst, attrs=None):
    """Create a repr from an instance of a class

    Args:
        inst: The class instance we are generating a repr of
        attrs: The attributes that should appear in the repr
    """
    # type: (object, Sequence[str]) -> str
    if attrs is None:
        attrs = []
    arg_str = ", ".join("%s=%r" % (a, getattr(inst, a)) for a in attrs)
    repr_str = "%s(%s)" % (inst.__class__.__name__, arg_str)
    return repr_str


def make_call_types(f, locals_d):
    """Make a call_types dictionary that describes what arguments to pass to f

    Args:
        f: The function to inspect for argument names (without self)
        locals_d: A dictionary of locals to lookup annotation definitions in
    """
    # type: (Callable, Dict) -> OrderedDict
    args = [k for k in inspect.getargspec(f).args if k != "self"]
    if not getattr(f, "__annotations__", None):
        # Make some from the type comment if there is one
        annotations = make_annotations(f, locals_d)
    else:
        annotations = f.__annotations__
    call_types = OrderedDict()
    for a in args:
        call_types[a] = annotations[a]
    return call_types
