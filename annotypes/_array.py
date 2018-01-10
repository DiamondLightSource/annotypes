from ._typing import TYPE_CHECKING, overload, Sequence, TypeVar, Generic

if TYPE_CHECKING:  # pragma: no cover
    from typing import Union, Type

T = TypeVar("T")


def array_type(cls):
    # type: (Type[Array[T]]) -> Type[T]
    type_args = getattr(cls, "__args__", ())
    assert type_args, "Expected Array[<typ>](...), got Array[%s](...)" % (
        ", ".join(repr(x) for x in type_args))
    return type_args[0]


class Array(Sequence[T], Generic[T]):
    """Wrapper that takes a sequence and provides immutable access to it"""

    def __len__(self):
        # type () -> int
        return len(self.seq)

    def __init__(self, seq=()):
        self.seq = seq  # type: Sequence[T]
        orig_class = getattr(self, "__orig_class__", None)
        assert orig_class, "You should instantiate Array[<typ>](...)"
        self.typ = array_type(orig_class)
        if hasattr(seq, "dtype"):
            assert seq.dtype == self.typ, \
                "Expected numpy array with type %s, got %s" % (self.typ, seq)

    @overload
    def __getitem__(self, idx):  # pragma: no cover
        # type: (int) -> T
        pass

    @overload
    def __getitem__(self, s):  # pragma: no cover
        # type: (slice) -> Sequence[T]
        pass

    def __getitem__(self, item):
        return self.seq[item]

    def __repr__(self):
        return repr(self.seq)


def to_array(typ, seq=None):
    # type: (Type[Array[T]], Union[Array[T], Sequence[T], T]) -> Array[T]
    if seq is None:
        return typ()
    elif isinstance(seq, Array):
        expected = array_type(typ)
        assert expected == seq.typ, \
            "Expected Array[%s], got Array[%s]" % (expected, seq.typ)
        return seq
    elif isinstance(seq, str) or not isinstance(seq, Sequence):
        # Wrap it in a list as it should be a sequence
        return typ([seq])
    else:
        return typ(seq)
