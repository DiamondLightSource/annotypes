from collections import OrderedDict
import numpy as np
import unittest

from enum import Enum

from annotypes import Anno, Array, Mapping, Union, Sequence, Any, \
    Serializable, deserialize_object, serialize_object, FrozenOrderedDict, \
    json_encode, json_decode

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


with Anno("A DSArray"):
    ADSArray = Array[DummySerializable]
UDSArray = Union[ADSArray, Sequence[DummySerializable]]


@Serializable.register_subclass("empty:1.0")
class EmptySerializable(Serializable):
    pass


@Serializable.register_subclass("nested:1.0")
class NestedSerializable(Serializable):
    boo = None
    dsarray = None

    def __init__(self, boo, dsarray):
        # type: (ABoo, UDSArray) -> None
        self.boo = ABoo(boo)
        self.dsarray = ADSArray(dsarray)


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
        assert self.s["typeid"] == "foo:1.0"

    def test_iter(self):
        assert list(self.s) == ['boo', 'bar', 'NOT_CAMEL']

    def test_serialize(self):
        x = serialize_object(self.s)
        assert x == self.expected
        x = serialize_object(ADSArray(self.s))
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

    def test_frozen_dict(self):
        items = [("typeid", "me"), ("a", 1), ("b", "two")]
        d = FrozenOrderedDict(items)
        assert list(d) == list(d.keys()) == ["typeid", "a", "b"]
        assert d.items() == list(d.iteritems()) == items
        assert d.values() == list(d.itervalues()) == ["me", 1, "two"]
        with self.assertRaises(TypeError):
            d["a"] = 2
        with self.assertRaises(TypeError):
            del d["a"]
        with self.assertRaises(TypeError):
            d.pop("a")
        with self.assertRaises(TypeError):
            d.popitem()
        with self.assertRaises(TypeError):
            d.setdefault("a", 33)
        with self.assertRaises(TypeError):
            d.update({"a": 33})
        with self.assertRaises(TypeError):
            d.clear()
        with self.assertRaises(TypeError):
            d.copy()
        with self.assertRaises(TypeError):
            d.fromkeys(("a", "b", "c"))

    def test_json_numpy_array(self):
        s1 = DummySerializable(3, {}, np.array([3, 4]))
        assert json_encode(s1) == \
            '{"typeid": "foo:1.0", "boo": 3, "bar": {}, "NOT_CAMEL": [3, 4]}'

    def test_exception_serialize(self):
        s = json_encode({"message": ValueError("Bad result")})
        assert s == '{"message": "ValueError: Bad result"}'

    def test_enum_serialize(self):
        class MyEnum(Enum):
            ME = "me"

        s = json_encode({"who": MyEnum.ME})
        assert s == '{"who": "me"}'

    def test_serializable_not_setting_attr(self):
        class NoAttr(Serializable):
            def __init__(self, boo):
                # type: (ABoo) -> None
                self.bad = boo

        o = NoAttr(3)
        assert o.bad == 3
        with self.assertRaises(KeyError):
            o["bad"]
        with self.assertRaises(KeyError):
            o["boo"]
        o.boo = 3
        assert o["boo"] == 3

    def test_json_decode(self):
        d = json_decode('{"a": 1, "b": 2}')
        assert list(d) == ["a", "b"]
        assert d.values() == [1, 2]

    def test_json_decode_not_dict(self):
        with self.assertRaises(ValueError):
            json_decode('[1, 2]')

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

    def test_to_dict_nested(self):

        n = NestedSerializable(13, self.s)

        expected = OrderedDict(typeid="nested:1.0")
        expected["boo"] = 13
        expected["dsarray"] = [self.expected]

        assert n.to_dict() == expected
