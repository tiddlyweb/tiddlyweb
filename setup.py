"""
Try to setup tiddlyweb.
Seem to be missing some details on how to make
this the best it can be.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from tiddlyweb import __version__ as VERSION

setup(name = 'tiddlyweb',
        version = VERSION,
        description = 'An optionally headless, extensible RESTful datastore for tiddlers: bits of stuff.',
        author = 'Chris Dent',
        author_email = 'cdent@peermore.com',
        url = 'http://tiddlyweb.com/',
        download_url = 'http://tiddlyweb.peermore.com/dist/',
        packages = ['tiddlyweb', 'tiddlyweb.filters', 'tiddlyweb.model', 'tiddlyweb.wikitext', 'tiddlyweb.serializations', 'tiddlyweb.stores', 'tiddlyweb.web', 'tiddlyweb.web.challengers', 'tiddlyweb.web.extractors', 'tiddlyweb.web.handler', ],
        scripts = ['twanager',],
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['selector', 'simplejson', 'html5lib', 'cherrypy'],
        include_package_data = True,
        )
