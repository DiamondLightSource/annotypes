Change Log
==========
All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

`Unreleased`_
-------------

Added:

- Nothing yet

`0-7`_ - 2018-04-24
-------------------

Fixed:
- make_annotations now always returns a dict

`0-6`_ - 2018-04-23
-------------------

Added:
- Add make_annotations to public API, and allow globals_d to be optional

`0-5`_ - 2018-02-16
-------------------

Added:

- Support for *args and **kwargs annotations
- Support for bare Any as return type
- Support for setting Anno.default in constructor
- Support for Array.__eq__

Changed:

- Annotation creation now only takes into account globals, not locals

Fixed:

- WithCallTypes subclasses may now also subclass Generic
- Array handling of numpy ndarrays better
- WithCallTypes subclasses with no __init__ now works
- Repr on instance where not all call_types are stored attributes now works


`0-4`_ - 2018-01-10
-------------------

Fixed:

- Example name that may cause Pycharm to fail
- Allow to_array to take sequence=None

`0-3`_ - 2018-01-04
-------------------

Added:

- Support for Any

`0-2`_ - 2018-01-04
-------------------

Added:

- Support for Mapping

`0-1-1`_ - 2018-01-02
---------------------

Fixed:

- Fixed PyPI packaging

0-1 - 2018-01-02
----------------

Initial release

.. _Unreleased: https://github.com/dls-controls/annotypes/compare/0-7...HEAD
.. _0-7: https://github.com/dls-controls/annotypes/compare/0-6...0-7
.. _0-6: https://github.com/dls-controls/annotypes/compare/0-5...0-6
.. _0-5: https://github.com/dls-controls/annotypes/compare/0-4...0-5
.. _0-4: https://github.com/dls-controls/annotypes/compare/0-3...0-4
.. _0-3: https://github.com/dls-controls/annotypes/compare/0-2...0-3
.. _0-2: https://github.com/dls-controls/annotypes/compare/0-1-1...0-2
.. _0-1-1: https://github.com/dls-controls/annotypes/compare/0-1...0-1-1
