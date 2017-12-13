import re
import tokenize
import inspect
import sys
from collections import OrderedDict

from ._type_checking import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence, Callable, Dict, List


type_re = re.compile('^# type: ([^-]*)( -> (.*))?$')


def getargspec(f):
    if sys.version_info < (3,):
        return inspect.getargspec(f)
    else:
        return inspect.getfullargspec(f)


def make_annotations(f, locals_d):
    # type: (Callable, Dict) -> Dict[str, str]
    """Create an annotations dictionary from Python2 type comments

    http://mypy.readthedocs.io/en/latest/python2.html

    Args:
        f: The function to examine for type comments
        locals_d: The locals dictionary to get type idents from
    """
    lines, _ = inspect.getsourcelines(f)
    arg_spec = getargspec(f)
    args = [k for k in arg_spec.args if k != "self"]
    it = iter(lines)
    ret = {}
    for a in args:
        ret[a] = 'Any'
    names = []  # type: List[str]
    for token in tokenize.generate_tokens(lambda: next(it)):
        typ, string, start, end, line = token
        if typ == tokenize.COMMENT:
            found = type_re.match(string)
            if found:
                parts = found.groups()
                # Can't eval '...' in python2
                if parts[0] != "(...)":
                    types = eval(parts[0], locals_d, locals())
                    if isinstance(types, tuple):
                        # We got more than one argument, so add type comments
                        # to all args of the functions
                        ret.update(zip(args, types))
                    elif len(args) == 1:
                        # Only one argument
                        ret[args[0]] = types
                    else:
                        # We got a single argument, so just type the first ident
                        # on the line
                        ret[names[0]] = types
                names = []
        elif typ == tokenize.NAME:
            names.append(string)
    return ret


def make_repr(inst, attrs=None):
    # type: (object, Sequence[str]) -> str
    """Create a repr from an instance of a class

    Args:
        inst: The class instance we are generating a repr of
        attrs: The attributes that should appear in the repr
    """
    if attrs is None:
        attrs = []
    arg_str = ", ".join("%s=%r" % (a, getattr(inst, a)) for a in attrs)
    repr_str = "%s(%s)" % (inst.__class__.__name__, arg_str)
    return repr_str


def make_call_types(f, locals_d):
    # type: (Callable, Dict) -> Dict[str, str]
    """Make a call_types dictionary that describes what arguments to pass to f

    Args:
        f: The function to inspect for argument names (without self)
        locals_d: A dictionary of locals to lookup annotation definitions in
    """
    arg_spec = getargspec(f)
    args = [k for k in arg_spec.args if k != "self"]
    if not getattr(f, "__annotations__", None):
        # Make string annotations from the type comment if there is one
        annotations = make_annotations(f, locals_d)
    else:
        annotations = f.__annotations__
    call_types = OrderedDict()  # type: Dict[str, str]
    for a in args:
        call_types[a] = annotations[a]
    return call_types
