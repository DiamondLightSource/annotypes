from typing import TypeVar, Sequence, Generic, overload, Union, Type


T = TypeVar("T")


class Array(Generic[T], Sequence[T]):
    """Wrapper that takes a sequence and provides immutable access to it"""

    def __len__(self):
        # type () -> int
        return len(self.seq)

    def __init__(self, seq=()):
        self.seq = seq  # type: Sequence[T]
        orig_class = getattr(self, "__orig_class__", None)
        assert orig_class, "You should instantiate Array[<typ>](...)"
        type_args = getattr(orig_class, "__args__", ())
        assert type_args, "Expected Array[<typ>](...), got Array[%s](...)" % (
            ", ".join(repr(x) for x in type_args))
        self.typ = type_args[0]

    @overload
    def __getitem__(self, idx):
        # type: (int) -> T
        pass

    @overload
    def __getitem__(self, s):
        # type: (slice) -> Sequence[T]
        pass

    def __getitem__(self, item):
        return self.seq[item]

    def __repr__(self):
        return repr(self.seq)


def to_array(typ, seq):
    # type: (Type[Array[T]], Union[Array[T], Sequence[T], T]) -> Array[T]
    if isinstance(seq, Array):
        return seq
    elif isinstance(seq, str) or not isinstance(seq, Sequence):
        # Wrap it in a tuple as it should be a sequence
        return typ((seq,))
    else:
        return typ(seq)