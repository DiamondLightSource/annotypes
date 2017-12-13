from typing import TypeVar, Sequence, Generic, overload


T = TypeVar("T", str, bool, int, float, covariant=True)


def error_message(*args):
    formatted_args = ", ".join(repr(a) for a in args)
    message = "Expected to_array(t1, t2, ...) or to_array(seq). " \
              "Got to_array(%s)" % formatted_args
    return message


class Array(Sequence[T], Generic[T]):
    """Wrapper that takes a sequence of str, bool, int or float and provides
    immutable access to it"""

    def __len__(self):
        # type () -> int
        return len(self.seq)

    def __init__(self, seq):
        self.seq = seq  # type: Sequence[T]
        self.typ = T

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


@overload
def to_array(seq):
    # type: (Sequence[T]) -> Array[T]
    pass


@overload
def to_array(*more):
    # type: (*T) -> Array[T]
    pass


def to_array(seq, *more):
    if isinstance(seq, T):
        # First element is a T, so assume *more is seq of T
        seq = (seq,) + more
    elif more:
        # Assume seq is iterable, so there should be no *more
        raise ValueError(error_message(seq, *more))
    assert isinstance(seq, Sequence), "%s is not a sequence" % (seq,)
    return Array(seq)
