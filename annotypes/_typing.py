try:
    from typing import (
        TYPE_CHECKING, TypeVar, Sequence, Union, Optional, Generic, overload
    )
except ImportError:
    from ._fake_typing import (  # type: ignore
        TYPE_CHECKING, TypeVar, Sequence, Union, Optional, Generic, overload
    )
