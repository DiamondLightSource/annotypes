AnnoTypes
=========

|build_status| |coverage|

Adding annotations to Python types while still being compatible with mypy_ and PyCharm_

You can write things like:

.. code:: python

    from annotypes import Anno, WithCallTypes

    with Anno("The exposure to be active for"):
        Exposure = float
    with Anno("The full path to the text file to write"):
        Path = str

    class Simple(WithCallTypes):
        def __init__(self, exposure, path="/tmp/file.txt"):
            # type: (Exposure, Path) -> None
            self.exposure = exposure
            self.path = path


or the Python3 alternative:

.. code:: python

    from annotypes import Anno, WithCallTypes

    with Anno("The exposure to be active for"):
        Exposure = float
    with Anno("The full path to the text file to write"):
        Path = str

    class Simple(WithCallTypes):
        def __init__(self, exposure: Exposure, path: Path = "/tmp/file.txt"):
            self.exposure = exposure
            self.path = path


And at runtime see what you should pass to call it and what it will return:

.. code:: pycon

    >>> from annotypes.py2_examples.simple import Simple
    >>> list(Simple.call_types)
    ['exposure', 'path']
    >>> Simple.call_types['exposure']
    Anno(name='Exposure', typ=<type 'float'>, description='The exposure to be active for')
    >>> Simple.return_type
    Anno(name='Instance', typ=<class 'annotypes.py2_examples.simple.Simple'>, description='Class instance')


For more examples see the `Python 2 examples`_ or `Python 3 examples`_.

.. |build_status| image:: https://travis-ci.org/dls-controls/annotypes.svg?branch=master
    :target: https://travis-ci.org/dls-controls/annotypes
    :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/dls-controls/annotypes/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/dls-controls/annotypes
    :alt: Test coverage

.. _mypy:
    http://mypy.readthedocs.io/en/latest/introduction.html

.. _PyCharm:
    https://www.jetbrains.com/help/pycharm/type-hinting-in-pycharm.html

.. _Python 2 examples:
    https://github.com/dls-controls/annotypes/tree/master/annotypes/py2_examples

.. _Python 3 examples:
    https://github.com/dls-controls/annotypes/tree/master/annotypes/py3_examples
