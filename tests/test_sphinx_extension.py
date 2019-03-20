import unittest
from collections import OrderedDict

from annotypes.sphinxext.call_types import skip_member, process_docstring
from annotypes.sphinxext.call_types import setup as sphinxsetup

from annotypes import Anno, Array, Mapping, Union, Sequence, Any, \
    Serializable, deserialize_object


class MyCallTypesClass:
    call_types = {}

    def __init__(self):
        pass


class MyReturnTypeClass:
    return_type = {}

    def __init__(self):
        pass


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
    foo = None

    def __init__(self, boo, bar, foo):
        # type: (ABoo, ABar, UNotCamel) -> None
        self.set_boo(boo)
        self.set_bar(bar)
        self.set_foo(foo)

    def set_boo(self, boo):
        self.boo = boo

    def set_bar(self, bar):
        d = OrderedDict()
        for k, v in bar.items():
            if k != "typeid":
                d[k] = deserialize_object(v)
        self.bar = d

    def set_foo(self, c):
        self.foo = ANotCamel(c)


class TestSphinxExtension(unittest.TestCase):

    def test_skip_member_doesnt_skip(self):
        result = skip_member("app", "what", "name", "obj", "skip", "options")
        assert result is None

    def test_skip_member_doesnt_skip_calltypes(self):
        obj = MyCallTypesClass()
        result = skip_member("app", "what", "name", obj, "skip", "options")
        assert result is False

    def test_skip_member_doesnt_skip_returntype(self):
        obj = MyReturnTypeClass()
        result = skip_member("app", "what", "name", obj, "skip", "options")
        assert result is False

    def test_skip_member_skips_gorg(self):
        name = "_gorg"
        obj = MyCallTypesClass()
        result = skip_member("app", "what", name, obj, "skip", "options")
        assert result is None

    def test_process_docstring(self):

        d = {'a': 42, 'b': 42}
        foo = [42, 42]
        s = DummySerializable(3, d, foo)

        lines = []

        expected_lines = [':param boo: A Boo',
                          ':type boo: int',
                          '',
                          ':param bar: A Bar',
                          '',
                          ':param foo: A Not Camel',
                          ':type foo: int',
                          '',
                          ':returns: Class instance',
                          ':rtype: DummySerializable']

        process_docstring("app", "what", "name", s, "options", lines)

        assert lines == expected_lines

    def test_process_docstring_no_calltypes(self):

        bar = {'a': 42, 'b': 42}
        foo = [42, 42]
        s = DummySerializable(3, bar, foo)

        lines = [':type line to stop call types']

        expected_lines = [':type line to stop call types',
                          ':returns: Class instance',
                          ':rtype: DummySerializable']

        process_docstring("app", "what", "name", s, "options", lines)

        assert lines == expected_lines

    def test_process_docstring_no_returntypes(self):

        bar = {'a': 42, 'b': 42}
        foo = [42, 42]
        s = DummySerializable(3, bar, foo)

        lines = [':rtype line to stop return types']

        expected_lines = [':rtype line to stop return types',
                          ':param boo: A Boo',
                          ':type boo: int',
                          '',
                          ':param bar: A Bar',
                          '',
                          ':param foo: A Not Camel',
                          ':type foo: int',
                          '']

        process_docstring("app", "what", "name", s, "options", lines)

        print lines

        assert lines == expected_lines

    def test_setup(self):

        class DummyApp:

            connections = {}

            def __init__(self):
                pass

            def connect(self, key, item):
                self.connections[key] = item

        app = DummyApp()

        # Call the sphinx extension 'setup' function.
        # Can't leave it called as just 'setup' as the tests try to call it
        # when they are setup, and it breaks
        sphinxsetup(app)

        assert DummyApp.connections['autodoc-skip-member'] == skip_member
        assert DummyApp.connections['autodoc-process-docstring'] == process_docstring

