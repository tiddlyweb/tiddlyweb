"""
Setup file for packaging TiddlyWeb
"""

import sys
import os

from setuptools import setup, find_packages

from tiddlyweb import __version__ as VERSION

CLASSIFIERS = """
Environment :: Web Environment
License :: OSI Approved :: BSD License
Operating System :: OS Independent
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.3
Topic :: Internet :: WWW/HTTP :: WSGI :: Application
""".strip().splitlines()


META = {
    'name': 'tiddlyweb',
    'version': VERSION,
    'description': 'An optionally headless, extensible HTTP datastore for tiddlers: bits of stuff.',
    'long_description': open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    'author': 'Chris Dent',
    'author_email': 'cdent@peermore.com',
    'url': 'http://pypi.python.org/pypi/tiddlyweb',
    'packages': find_packages(exclude=['test', 'test.*', 'profile']),
    'scripts': ['twanager'],
    'platforms': 'Posix; MacOS X; Windows',
    'classifiers': CLASSIFIERS,
    'install_requires': ['setuptools',
        'httpexceptor>=1.3.0',
        'selector>=0.10.0',
        'simplejson',
        'html5lib',
        'python-mimeparse>0.1.3'
    ],
    'extras_require': {
        'testing': ['pytest', 'httplib2', 'PyYAML', 'wsgi-intercept>=0.6.0']
    },
    'include_package_data': True,
    'zip_safe': False,
}


if __name__ == '__main__':
    setup(**META)
