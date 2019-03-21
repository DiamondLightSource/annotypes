Contributing
============

Contributions and issues are most welcome! All issues and pull requests are
handled through github on the `dls_controls repository`_. Also, please check for
any existing issues before filing a new one. If you have a great idea but it
involves big changes, please file a ticket before making a pull request! We
want to make sure you don't spend your time coding something that might not fit
the scope of the project.

.. _dls_controls repository: https://github.com/dls-controls/annotypes/issues

Running the tests
-----------------

To get the source source code and run the unit tests, run::

    $ git clone git://github.com/dls-controls/annotypes.git
    $ cd annotypes
    $ virtualenv --no-site-packages -p /path/to/python2.7 venv
    $ . venv/bin/activate
    $ pip install -r requirements/test.txt
    $ pytest tests

While 100% code coverage does not make a library bug-free, it significantly
reduces the number of easily caught bugs! Please make sure coverage is at 100%
before submitting a pull request!

Code Styling
------------
Please arrange imports with the following style

.. code-block:: python

    # Standard library imports
    import os

    # Third party package imports
    from mock import patch

    # Local package imports
    from annotypes.version import __version__

Please follow `Google's python style`_ guide wherever possible.

.. _Google's python style: https://google.github.io/styleguide/pyguide.html

Release Checklist
-----------------

Before a new release, please go through the following checklist:

* Bump version in annotypes/version.py
* Add a release note in CHANGELOG.rst
* Create a new github compare link at the bottom of CHANGELOG.rst for the release and update the _Unreleased link with the new release number
* Git tag the version with an annotated tag containing the relevant release notes section
* Push to github and travis will make a release on pypi

