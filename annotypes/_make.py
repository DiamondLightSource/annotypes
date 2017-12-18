import re
import tokenize
import inspect
import sys

from ._type_checking import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence, Callable, Dict, List, Any


type_re = re.compile('^# type: ([^-]*)( -> (.*))?$')


def getargspec(f):
    if sys.version_info < (3,):
        return inspect.getargspec(f)
    else:
        return inspect.getfullargspec(f)


def make_annotations(f, locals_d, globals_d):
    # type: (Callable, Dict, Dict) -> Dict[str, Any]
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
    types = []  # type: List
    for token in tokenize.generate_tokens(lambda: next(it)):
        typ, string, start, end, line = token
        if typ == tokenize.COMMENT:
            found = type_re.match(string)
            if found:
                parts = found.groups()
                # (...) is used to represent all the args so far
                if parts[0] != "(...)":
                    ob = eval(parts[0], globals_d, locals_d)
                    if isinstance(ob, tuple):
                        # We got more than one argument
                        types += list(ob)
                    else:
                        # We got a single argument
                        types.append(ob)
                if parts[1]:
                    # Got a return, done
                    ob = eval(parts[2], globals_d, locals_d)
                    assert len(args) == len(types), \
                        "Args %r Types %r length mismatch" % (args, types)
                    ret = dict(zip(args, types))
                    ret["return"] = ob
                    return ret
    raise ValueError("Got to the end of the function without seeing ->")


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

