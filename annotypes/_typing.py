import sys

try:
    from typing import (
        TYPE_CHECKING, TypeVar, Sequence, Union, Optional, Generic,
        overload, Mapping, Any
    )
    if sys.version_info >= (3, 7):
        from abc import ABCMeta as GenericMeta
        from collections.abc import Mapping as MappingType
        NEW_TYPING = True
    else:
        from typing import GenericMeta, Mapping as MappingType
        NEW_TYPING = False
except ImportError:
    if sys.version_info < (3, 0):
        from ._fake_typing import (
            TYPE_CHECKING, TypeVar, Sequence, Union, Optional, Generic,
            overload, Mapping, Any, GenericMeta
        )
    else:
        raise

sys_issubclass = issubclass
if sys.version_info >= (3, 7):
    # noinspection PyShadowingBuiltins
    def issubclass(c1, c2):
        if c1 is Any:
            return False
        else:
            return sys_issubclass(c1, c2)
else:
    # noinspection PyShadowingBuiltins
    def issubclass(c1, c2):
        return sys_issubclass(c1, c2)
