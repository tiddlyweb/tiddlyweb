"""
Try to setup tiddlyweb.
Seem to be missing some details on how to make
this the best it can be.
"""

import os

from setuptools import setup

from tiddlyweb import __version__ as VERSION

setup(name = 'tiddlyweb',
        version = VERSION,
        description = 'An optionally headless, extensible RESTful datastore for tiddlers: bits of stuff.',
        long_description=file(os.path.join(os.path.dirname(__file__), 'README')).read(),
        author = 'Chris Dent',
        author_email = 'cdent@peermore.com',
        url = 'http://pypi.python.org/pypi/tiddlyweb',
        packages = ['tiddlyweb', 'tiddlyweb.filters', 'tiddlyweb.model', 'tiddlyweb.wikitext', 'tiddlyweb.serializations', 'tiddlyweb.stores', 'tiddlyweb.web', 'tiddlyweb.web.challengers', 'tiddlyweb.web.extractors', 'tiddlyweb.web.handler', ],
        scripts = ['twanager',],
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['setuptools', 'selector', 'simplejson', 'html5lib', 'cherrypy'],
        include_package_data = True,
        )
