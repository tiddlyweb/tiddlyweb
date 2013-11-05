"""
Setup file for packaging TiddlyWeb
"""

import sys
import os

from setuptools import setup, find_packages

from tiddlyweb import __version__ as VERSION

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
    'install_requires': ['setuptools',
        'httpexceptor>=1.3.0',
        #'selector', # selector is currently in flux
        'git+https://github.com/cdent/selector.git@python2and3#egg=selector>=0.9',
        'simplejson',
        'html5lib',
        'python-mimeparse>0.1.3'],
    'extras_require': {
        'testing': ['pytest', 'httplib2', 'PyYAML', 'wsgi-intercept>=0.6.0']
    },
    'include_package_data': True,
    'zip_safe': False,
}


if __name__ == '__main__':
    setup(**META)
