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
        description = 'An optionally headless, extensible RESTful datastore for TiddlyWiki and pretty much anything else.',
        author = 'Chris Dent',
        author_email = 'cdent@peermore.com',
        url = 'http://tiddlyweb.peermore.com/',
        download_url = 'http://tiddlyweb.peermore.com/dist/',
        packages = ['tiddlyweb', 'tiddlyweb.filters', 'tiddlyweb.model', 'tiddlyweb.serializations', 'tiddlyweb.stores', 'tiddlyweb.web', 'tiddlyweb.web.challengers', 'tiddlyweb.web.extractors', 'tiddlyweb.web.handler', 'cherrypy', 'cherrypy.wsgiserver'],
        scripts = ['twanager',],
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['selector', 'simplejson', 'BeautifulSoup', 'wikklytext', 'html5lib'],
        include_package_data = True,
        )




