import inspect

from .typing import Optional
from ._make import make_repr


class Anno(object):
    def __init__(self, description):
        """Annotate a type with run-time accessible metadata

        Args:
            description: A one-line description for the argument
        """
        # type: (str, Optional[str]) -> None
        self._locals = set()
        self.typ = None
        self.name = None
        self.description = description
        # TODO: add min, max, maybe widget

    def __call__(self, *args, **kwargs):
        """Pass calls through to our underlying type"""
        return self.typ(*args, **kwargs)

    def __repr__(self):
        attrs = ["typ", "description"]
        return make_repr(self, attrs)

    def __enter__(self):
        # Store the current frame locals so we can work out what has been
        # defined
        frame = inspect.currentframe(1)
        self._locals = set(frame.f_locals)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            return False
        frame = inspect.currentframe(1)
        defined = set(frame.f_locals) - self._locals
        assert len(defined) == 1, \
            "Expected a single type to be defined, got %s" % list(defined)
        self.name = defined.pop()
        self.typ = frame.f_locals[self.name]
        frame.f_locals[self.name] = self
