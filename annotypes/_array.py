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

    def __init__(self, seq=None):
        if seq is None:
            seq = []
        self.seq = seq  # type: Sequence[T]
        orig_class = getattr(self, "__orig_class__", None)
        assert orig_class, "You should instantiate Array[<typ>](...)"
        self.typ = array_type(orig_class)
        if hasattr(seq, "dtype"):
            assert self.typ == seq.dtype, \
                "Expected numpy array with dtype %s, got %r with dtype %s" % (
                    self.typ, seq, seq.dtype)

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

    def __eq__(self, other):
        # type: (object) -> bool
        if isinstance(other, Array):
            return self.typ == other.typ and self.seq == other.seq
        else:
            return self.seq == other

    def __repr__(self):
        return "Array(%r)" % (self.seq,)


def to_array(typ, seq=None):
    # type: (Type[Array[T]], Union[Array[T], Sequence[T], T]) -> Array[T]
    expected = array_type(typ)
    if hasattr(seq, "dtype"):
        # It's a numpy array
        return typ(seq)
    elif isinstance(seq, Array):
        assert expected == seq.typ, \
            "Expected Array[%s], got Array[%s]" % (expected, seq.typ)
        return seq
    elif seq is None:
        return typ()
    elif isinstance(seq, str) or not isinstance(seq, Sequence):
        # Wrap it in a list as it should be a sequence
        return typ([seq])
    elif len(seq) == 0:
        # Zero length array
        return typ()
    else:
        # It's a sequence, so assume it's ok
        return typ(seq)
