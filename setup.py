"""
Pypher
------


"""
import sys
from setuptools import setup, find_packages


install_requires = [
    'six'
]

# get the version information
exec(open('pypher/version.py').read())

setup(
    name = 'vertex',
    packages = find_packages(),
    version = __version__,
    description = 'Cypher Statement Builder for Python',
    url = 'https://github.com/emehrkay/pypher',
    author = 'Mark Henderson',
    author_email = 'emehrkay@gmail.com',
    long_description = __doc__,
    install_requires = install_requires,
    classifiers = [
    ],
    test_suite = 'pypher.test',
)
