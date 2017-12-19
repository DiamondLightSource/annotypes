import unittest
import sys
import collections

from annotypes import WithCallTypes, Array, Sequence


class TestAnnotypes(unittest.TestCase):
    def test_no_args_base_repr(self):

        class MyClass(WithCallTypes):
            pass

        assert repr(MyClass()) == "MyClass()"


class TestSimple(unittest.TestCase):
    def setUp(self):
        if sys.version_info < (3,):
            from annotypes.py2_examples.simple import Simple
        else:
            from annotypes.py3_examples.simple import Simple
        self.cls = Simple

    def test_simple(self):
        ct = self.cls.call_types
        assert list(ct) == ["exposure", "path"]
        assert ct["exposure"].description == "The exposure to be active for"
        assert ct["exposure"].typ(3) == 3.0
        assert ct["path"].typ == str
        assert ct["path"].default == "/tmp/file.txt"
        assert self.cls.return_type.typ == self.cls
        fname = "/tmp/fname.txt"
        inst = self.cls(0.1, fname)
        assert repr(inst) == \
            "Simple(exposure=0.1, path='/tmp/fname.txt')"
        inst.write_data("something")
        with open(fname) as f:
            assert f.read() == "Data: something\n"


class TestManyArgs(unittest.TestCase):
    def setUp(self):
        if sys.version_info < (3,):
            from annotypes.py2_examples.manyargs import ManyArgs
        else:
            from annotypes.py3_examples.manyargs import ManyArgs
        self.cls = ManyArgs

    def test_many_args(self):
        ct = self.cls.call_types
        assert list(ct) == \
            ['axes', 'start', 'stop', 'size', 'units', 'alternate']
        assert ct["start"].typ == float
        assert ct["start"].is_array is True
        assert ct["units"].typ == str
        assert ct["units"].is_array is True
        assert ct["units"].default.seq == ("mm",)
        assert ct["alternate"].description == \
            "Whether to reverse on alternate runs"
        assert ct["alternate"].default is False
        assert self.cls.return_type.typ == self.cls
        inst = self.cls("x", 0, 1, 10)
        assert repr(inst) == \
            "ManyArgs(axes=('x',), start=(0,), stop=(1,), size=10, units=('mm',), alternate=False)"
        assert inst.start.typ == float


class TestComposition(unittest.TestCase):
    def setUp(self):
        if sys.version_info < (3,):
            from annotypes.py2_examples.composition import (
                CompositionClass, composition_func)
        else:
            from annotypes.py3_examples.composition import (
                CompositionClass, composition_func)
        self.cls = CompositionClass
        self.f = composition_func

    def test_composition_class(self):
        ct = self.cls.call_types
        assert list(ct) == ['exposure', 'path']
        assert ct["exposure"].description == \
            "The exposure to be active for"
        assert ct["exposure"].typ == float
        assert ct["path"].typ == str
        assert self.cls.return_type.typ == self.cls
        inst = self.cls(0.1, "/tmp/fname.txt")
        assert repr(inst) == \
            "CompositionClass(exposure=0.1, path='/tmp/fname.txt')"

    def test_composition_func(self):
        ct = self.f.call_types
        assert list(ct) == ['exposure', 'prefix']
        assert ct["exposure"].description == \
            "The exposure to be active for"
        assert ct["exposure"].typ == float
        assert ct["prefix"].default is None
        assert ct["prefix"].description == \
            "The path prefix for the list of writers"
        assert self.f.return_type.typ.__name__ == "Simple"
        assert self.f.return_type.is_array is True
        assert self.f.return_type.default is None
        insts = self.f(0.1, "/tmp")
        assert insts.__class__.__name__ == "Array"
        assert insts.typ.__name__ == "Simple"
        assert repr(insts[0]) == \
            "Simple(exposure=0.1, path='/tmp/one')"


class TestEnum(unittest.TestCase):
    def setUp(self):
        if sys.version_info < (3,):
            from annotypes.py2_examples.enumtaker import EnumTaker, Status
        else:
            from annotypes.py3_examples.enumtaker import EnumTaker, Status
        self.cls = EnumTaker
        self.e = Status

    def test_enum(self):
        ct = self.cls.call_types
        assert list(ct) == ['status']
        assert ct["status"].description == "The status"
        assert ct["status"].typ == self.e
        assert self.e['good'].name == 'good'
        assert self.cls.return_type.typ == self.cls
        inst = self.cls(self.e.good)
        assert repr(inst) == \
            "EnumTaker(status=<Status.good: 0>)"


class TestReuse(unittest.TestCase):
    def setUp(self):
        if sys.version_info < (3,):
            from annotypes.py2_examples.reusecls import ReuseCls, Simple
        else:
            from annotypes.py3_examples.reusecls import ReuseCls, Simple
        self.cls = ReuseCls
        self.s = Simple

    def test_reuse(self):
        assert list(self.cls.call_types) == []
        ct = self.cls.validate.call_types
        assert list(ct) == ["params"]
        assert ct["params"].description == "Parameters to take"
        assert ct["params"].typ == self.s
        assert self.cls.validate.return_type.typ == self.s
        ct = self.cls.configure.call_types
        assert list(ct) == ["params"]
        inst = self.cls()
        params = self.s(0.1)
        inst.validate(params)
        assert params.exposure == 0.4
        inst.configure(params)


class TestArray(unittest.TestCase):
    def test_sequence(self):
        assert issubclass([].__class__, collections.Sequence)
        assert isinstance([], collections.Sequence)
        assert issubclass([].__class__, Sequence)
        assert isinstance([], Sequence)

    def test_array(self):
        with self.assertRaises(AssertionError):
            Array()
        self.a = Array[int]()
        assert isinstance(self.a, Array)
        assert self.a.typ == int
        self.b = Array[float]()
        assert isinstance(self.b, Array)
        assert self.a.typ == int
        import numpy as np
        self.c = Array[int](np.arange(3))
        assert isinstance(self.c, Array)
        assert self.c.typ == int
        assert repr(self.c) == "array([0, 1, 2])"


class TestTable(unittest.TestCase):
    def setUp(self):
        if sys.version_info < (3,):
            from annotypes.py2_examples.table import Manager, LayoutTable
        else:
            from annotypes.py3_examples.table import Manager, LayoutTable
        self.cls = Manager
        self.t = LayoutTable

    def test_table(self):
        assert list(self.cls.call_types) == []
        ct = self.cls.set_layout.call_types
        assert list(ct) == ["value"]
        assert ct["value"].description == "The layout table to act on"
        assert ct["value"].typ == self.t
        assert self.cls.set_layout.return_type is None
        inst = self.cls()
        layout = self.t(Array[str](["BLOCK"]),
                        Array[str](["MRI"]),
                        Array[float]([0.5]),
                        Array[float]([2.5]),
                        Array[float]([True]))
        inst.set_layout(layout)
        assert list(inst.layout.mri) == ["MRI"]
        assert repr(inst) == "Manager()"
        assert repr(layout) == "LayoutTable(name=['BLOCK'], mri=['MRI'], x=[0.5], y=[2.5], visible=[True])"


if __name__ == "__main__":
    unittest.main(verbosity=2)
