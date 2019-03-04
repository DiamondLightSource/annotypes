from collections import OrderedDict
import unittest

from annotypes import Anno, Array, Mapping, Union, Sequence, Any, \
    Serializable, deserialize_object, serialize_object


with Anno("A Boo"):
    ABoo = int
with Anno("A Bar"):
    ABar = Mapping[str, Any]
with Anno("A Not Camel"):
    ANotCamel = Array[int]
UNotCamel = Union[ANotCamel, Sequence[int]]


@Serializable.register_subclass("foo:1.0")
class DummySerializable(Serializable):
    boo = None
    bar = None
    NOT_CAMEL = None

    def __init__(self, boo, bar, NOT_CAMEL):
        # type: (ABoo, ABar, UNotCamel) -> None
        self.set_boo(boo)
        self.set_bar(bar)
        self.set_not(NOT_CAMEL)

    def set_boo(self, boo):
        self.boo = boo

    def set_bar(self, bar):
        d = OrderedDict()
        for k, v in bar.items():
            if k != "typeid":
                d[k] = deserialize_object(v)
        self.bar = d

    def set_not(self, c):
        self.NOT_CAMEL = ANotCamel(c)


@Serializable.register_subclass("empty:1.0")
class EmptySerializable(Serializable):
    pass


class TestSerialization(unittest.TestCase):

    def setUp(self):
        d = {'a': 42, 'b': 42}
        l = [42, 42]
        self.s = DummySerializable(3, d, l)
        expected = OrderedDict(typeid="foo:1.0")
        expected["boo"] = 3
        expected["bar"] = d
        expected["NOT_CAMEL"] = l
        self.expected = expected

    def test_to_dict_from_dict(self):
        assert self.expected == self.s.to_dict()
        n = DummySerializable.from_dict(self.expected)
        assert n.to_dict() == self.expected

    def test_get_item(self):
        assert self.s["boo"] == 3
        with self.assertRaises(KeyError):
            self.s["bad"]

    def test_iter(self):
        assert list(self.s) == ['boo', 'bar', 'NOT_CAMEL']

    def test_serialize(self):
        x = serialize_object(self.s)
        assert x == self.expected
        x = serialize_object([self.s])
        assert x == [self.expected]

    def test_no_args(self):
        self.expected["extra"] = "thing"
        with self.assertRaises(TypeError) as cm:
            deserialize_object(self.expected)
        assert str(cm.exception) == "foo:1.0 raised error: __init__() got an unexpected keyword argument 'extra'"

    def test_no_typeid(self):
        with self.assertRaises(TypeError) as cm:
            deserialize_object({})
        assert str(cm.exception) == "typeid not present in keys []"

    def test_bad_typeid(self):
        with self.assertRaises(TypeError) as cm:
            deserialize_object(dict(typeid="something_bad"))
        assert str(cm.exception) == "'something_bad' not a valid typeid"

    def test_deserialize(self):
        a = EmptySerializable()
        d = a.to_dict()
        b = deserialize_object(d, EmptySerializable)
        assert a.to_dict() == b.to_dict()

    def test_to_dict_children(self):
        children = OrderedDict()
        children["a"] = EmptySerializable().to_dict()
        children["b"] = EmptySerializable().to_dict()
        s = DummySerializable(3, children, [])
        expected = OrderedDict(typeid="foo:1.0")
        expected["boo"] = 3
        expected["bar"] = children
        expected["NOT_CAMEL"] = []

        assert expected == s.to_dict()

        n = DummySerializable.from_dict(expected)
        assert n.to_dict() == expected
