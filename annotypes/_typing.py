import sys

if sys.version_info < (3, 0):
    try:
        from typing import (
            TYPE_CHECKING, TypeVar, Sequence, Union, Optional, Generic,
            overload, Mapping
        )
    except ImportError:
        from ._fake_typing import (
            TYPE_CHECKING, TypeVar, Sequence, Union, Optional, Generic,
            overload, Mapping
        )
else:
    from typing import (
        TYPE_CHECKING, TypeVar, Sequence, Union, Optional, Generic,
        overload, Mapping
    )
