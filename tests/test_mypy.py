import unittest
import sys
import subprocess
import os


def mypy(path):
    p = subprocess.Popen(['mypy', path], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    return p.communicate()


class TestSimple(unittest.TestCase):
    def setUp(self):
        if sys.version_info < (3,):
            from annotypes.py2_examples.simple import Simple
        else:
            from annotypes.py3_examples.simple import Simple
        self.cls = Simple

    def test_mypy_good(self):
        if sys.version_info < (3,):
            return
        path = os.path.join(os.path.dirname(__file__), "mypy_good.py")
        stdout, stderr = mypy(path)
        assert not stdout
        assert not stderr

    def test_mypy_bad(self):
        if sys.version_info < (3,):
            return
        path = os.path.join(os.path.dirname(__file__), "mypy_bad.py")
        with open(os.path.join(os.path.dirname(__file__),
                               "mypy_bad_expected_errors.txt"), 'rb') as f:
            expected = f.read()
        stdout, stderr = mypy(path)
        assert stdout == expected
        assert not stderr
