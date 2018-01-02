import re
import os
from setuptools import setup, find_packages

module_name = "annotypes"


def get_version():
    """Extracts the version number from the version.py file.
    """
    VERSION_FILE = os.path.join(module_name, 'version.py')
    txt = open(VERSION_FILE).read()
    mo = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', txt, re.M)
    if mo:
        version = mo.group(1)
        bs_version = os.environ.get('MODULEVER', '0.0')
        assert bs_version == "0.0" or bs_version == version, \
            "Version {} specified by the build system doesn't match {} in " \
            "version.py".format(bs_version, version)
        return version
    else:
        raise RuntimeError('Unable to find version string in {0}.'
                           .format(VERSION_FILE))


packages = [x for x in find_packages() if x.startswith(module_name)]
setup(
    name=module_name,
    version=get_version(),
    description='Annotating type hints and comments with extra metatdata',
    long_description=open("README.rst").read(),
    url='https://github.com/dls-controls/annotypes',
    author='Tom Cobb',
    author_email='tom.cobb@diamond.ac.uk',
    keywords='',
    packages=packages,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    license='APACHE',
    install_requires=[],
    include_package_data=True,
    zip_safe=False,
)
