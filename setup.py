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
    'long_description': file(os.path.join(os.path.dirname(__file__), 'README')).read(),
    'author': 'Chris Dent',
    'author_email': 'cdent@peermore.com',
    'url': 'http://pypi.python.org/pypi/tiddlyweb',
    'packages': find_packages(exclude=['test', 'test.*', 'profile']),
    'scripts': ['twanager'],
    'platforms': 'Posix; MacOS X; Windows',
    'install_requires': ['setuptools',
        'httpexceptor',
        # modern Selector requires modern Python, so downgrade for older versions
        'selector' + ('<0.9.0' if (sys.version_info[0] == 2 and
                sys.version_info[1] < 6) else ''),
        'simplejson',
        'html5lib',
        'mimeparse',
        'cherrypy'],
    'extras_require': {
        'testing': ['pytest', 'httplib2', 'wsgi_intercept', 'PyYAML',
                'tiddlywebplugins.utils']
    },
    'include_package_data': True,
    'zip_safe': False,
}


if __name__ == '__main__':
    setup(**META)
