import json
import unittest

from annotypes import to_dict
from annotypes.typing import Union, List
from annotypes.py2_examples.simple import Simple
from annotypes.py2_examples.long import Long


class TestAnnotypes(unittest.TestCase):
    def test_simple(self):
        ct = Simple.call_types
        assert list(ct) == ["exposure", "path"]
        assert ct["exposure"].description == "The exposure to be active for"
        assert ct["path"].typ is str
        inst = Simple(0.1, "fname.txt")
        assert repr(inst) == \
            "Simple(exposure=0.1, path='fname.txt')"
        assert json.dumps(to_dict(inst)) == \
            '{"exposure": 0.1, "path": "fname.txt"}'

    def test_long(self):
        ct = Long.call_types
        assert list(ct) == \
            ['axes', 'units', 'start', 'stop', 'size', 'alternate']
        assert ct["alternate"].description == \
            "Whether to reverse on alternate runs"
        assert ct["units"].typ == Union[List[str], str]
        inst = Long("x", "mm", 0, 1, 10)
        assert repr(inst) == \
            "Long(axes=['x'], units=['mm'], start=[0], stop=[1], size=10, alternate=False)"
        assert json.dumps(to_dict(inst)) == \
            '{"axes": ["x"], "units": ["mm"], "start": [0], "stop": [1], "size": 10, "alternate": false}'
