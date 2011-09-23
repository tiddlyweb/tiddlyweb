"""
Setup file for packaging TiddlyWeb.
"""

import os

from setuptools import setup, find_packages

from tiddlyweb import __version__ as VERSION

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
        install_requires = ['setuptools',
            'selector',
            'simplejson',
            'html5lib',
            'mimeparse',
            'cherrypy'],
        include_package_data = True,
        zip_safe=False,
        )
