"""
Try to setup tiddlyweb.
Seem to be missing some details on how to make
this the best it can be.
"""

import os

from setuptools import setup, find_packages

from tiddlyweb import __version__ as VERSION

APP = ['macapp.py']

setup(name = 'tiddlyweb',
        version = VERSION,
        description = 'An optionally headless, extensible RESTful datastore for tiddlers: bits of stuff.',
        long_description=file(os.path.join(os.path.dirname(__file__), 'README')).read(),
        author = 'Chris Dent',
        author_email = 'cdent@peermore.com',
        url = 'http://pypi.python.org/pypi/tiddlyweb',
        packages = find_packages(exclude=['test', 'test.*', 'profile']),
        scripts = ['twanager',],
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['setuptools', 'selector', 'simplejson', 'html5lib', 'cherrypy'],
        include_package_data = True,
        app=APP,
        options={'py2app': {
            'argv_emulation': True,
            'resources': ['tiddlyweb/urls.map'],
            'packages': find_packages(exclude=['test', 'test.*', 'profile']),
            },
            },
        zip_safe=False,
        )
