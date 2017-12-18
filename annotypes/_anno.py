import sys

from ._type_checking import TYPE_CHECKING
from ._make import make_repr
from ._array import Array

if TYPE_CHECKING:
    from typing import Dict, Set, Tuple, Any


def caller_locals_globals():
    # type: () -> Tuple[Dict, Dict]
    """Return the frame object for the caller's stack frame."""
    try:
        raise ValueError
    except ValueError:
        caller_frame = sys.exc_info()[2].tb_frame.f_back.f_back
        return caller_frame.f_locals, caller_frame.f_globals


NO_DEFAULT = object()


class Anno(object):
    def __init__(self, description):
        # type: (str) -> None
        """Annotate a type with run-time accessible metadata

        Args:
            description: A one-line description for the argument
        """
        self._names_on_enter = None  # type: Set[str]
        self.default = NO_DEFAULT  # type: Any
        self.typ = None  # type: type
        self.name = None  # type: str
        self.is_array = None  # type: bool
        self.description = description  # type: str
        # TODO: add min, max, maybe widget

    def __call__(self, *args, **kwargs):
        """Pass calls through to our underlying type"""
        if self.is_array:
            return Array[self.typ](*args, **kwargs)
        else:
            return self.typ(*args, **kwargs)

    def __repr__(self):
        attrs = ["typ", "description"]
        return make_repr(self, attrs)

    def __enter__(self):
        # Store the current frame locals so we can work out what has been
        # defined
        self._names_on_enter = set(caller_locals_globals()[0])

    def _get_defined_name(self, locals_d):
        defined = set(locals_d) - self._names_on_enter
        assert len(defined) == 1, \
            "Expected a single type to be defined, got %s" % list(defined)
        self.name = defined.pop()

    def _get_type(self, typ):
        origin = getattr(typ, "__origin__", None)
        if origin == Array:
            # This is an array
            self.is_array = True
            self.typ = typ.__args__[0]
        elif origin is None:
            # This is a bare type
            self.is_array = False
            self.typ = typ
        else:
            raise ValueError("Cannot annotate a type with origin %r" % origin)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            return False
        locals_d = caller_locals_globals()[0]
        self._get_defined_name(locals_d)
        self._get_type(locals_d[self.name])
        locals_d[self.name] = self
