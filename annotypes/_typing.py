import sys

try:
    from typing import (
        TYPE_CHECKING, TypeVar, Sequence, Union, Optional, Generic,
        overload, Mapping, Any, GenericMeta
    )
except ImportError:
    if sys.version_info < (3, 0):
        from ._fake_typing import (
            TYPE_CHECKING, TypeVar, Sequence, Union, Optional, Generic,
            overload, Mapping, Any, GenericMeta
        )
    else:
        raise
