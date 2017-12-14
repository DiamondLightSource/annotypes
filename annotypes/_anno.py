import sys

from ._type_checking import TYPE_CHECKING
from ._make import make_repr

from typing import Union, Sequence

if TYPE_CHECKING:
    from typing import Dict, Set


def caller_locals():
    # type: () -> Dict
    """Return the frame object for the caller's stack frame."""
    try:
        raise ValueError
    except ValueError:
        return sys.exc_info()[2].tb_frame.f_back.f_back.f_locals


class Anno(object):
    def __init__(self, description):
        # type: (str) -> None
        """Annotate a type with run-time accessible metadata

        Args:
            description: A one-line description for the argument
        """
        self._names_on_enter = None  # type: Set[str]
        self.typ = None  # type: type
        self.name = None  # type: str
        self.is_array = None  # type: bool
        self.description = description  # type: str
        # TODO: add min, max, maybe widget

    def __call__(self, *args, **kwargs):
        """Pass calls through to our underlying type if it is simple"""
        return self.typ(*args, **kwargs)

    def __repr__(self):
        attrs = ["typ", "description"]
        return make_repr(self, attrs)

    def __enter__(self):
        # Store the current frame locals so we can work out what has been
        # defined
        self._names_on_enter = set(caller_locals())

    def _get_defined_name(self, locals_d):
        defined = set(locals_d) - self._names_on_enter
        assert len(defined) == 1, \
            "Expected a single type to be defined, got %s" % list(defined)
        self.name = defined.pop()

    def _get_type(self, typ):
        if getattr(typ, "__origin__", None) == Union:
            # the type we are interested in is the first parameter
            typ = typ.__args__[0]
        if getattr(typ, "__origin__", None) == Sequence:
            # This is an array
            self.is_array = True
            self.typ = typ.__args__[0]
        else:
            # This is a bare type
            self.is_array = False
            self.typ = typ

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            return False
        locals_d = caller_locals()
        self._get_defined_name(locals_d)
        self._get_type(locals_d[self.name])
        locals_d[self.name] = self
