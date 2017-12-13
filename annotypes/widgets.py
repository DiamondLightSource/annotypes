from ._type_checking import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List


WIDGETS = []  # type: List[str]
"""A list of the supported widgets"""

DEFAULT_WIDGET = {}  # type: Dict[type, str]
"""A mapping of a type to its default widget"""


def register_types(widget, *types):
    """Register a widget with the default types it should be used for"""
    assert widget not in WIDGETS, "Widget %s already registered" % widget
    WIDGETS.append(widget)
    for typ in types:
        DEFAULT_WIDGET[typ] = widget


TEXTINPUT = "textinput"
register_types(TEXTINPUT, str, int, float)

try:
    from enum import Enum
except ImportError:
    pass
else:
    COMBO = "combo"
    register_types(COMBO, Enum)


# Include all constants
__all__ = [x for x in list(locals()) if x.upper() == x]

