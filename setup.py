"""
Pypher
------

Pypher is graph abstraction layer that converts Python objects
to Cypher strings complete with bound parameters.
"""
import sys
from setuptools import setup, find_packages


install_requires = [
    'prompt_toolkit',
    'six'
]

# get the version information
exec(open('pypher/version.py').read())

setup(
    name = 'python_cypher',
    packages = find_packages(),
    version = __version__,
    description = 'Cypher Statement Builder for Python',
    url = 'https://github.com/emehrkay/pypher',
    author = 'Mark Henderson',
    author_email = 'emehrkay@gmail.com',
    long_description = __doc__,
    install_requires = install_requires,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'Environment :: Web Environment',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Operating System :: MacOS :: MacOS X',
    ],
    test_suite = 'pypher.test',
)
