"""
Try to setup tiddlyweb.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from tiddlyweb import __version__ as VERSION

setup(name = 'tiddlyweb',
        version = VERSION,
        description = 'An optionally headless, extensible RESTful datastore for TiddlyWiki',
        author = 'Chris Dent',
        author_email = 'cdent@peermore.com',
        url = 'http://svn.tiddlywiki.org/Trunk/association/serversides/tiddlyweb/core',
        packages = ['tiddlyweb', 'tiddlyweb.model', 'tiddlyweb.serializations', 'tiddlyweb.stores', 'tiddlyweb.web', 'tiddlyweb.web.challengers', 'tiddlyweb.web.extractors', 'tiddlyweb.web.handler', 'cherrypy', 'cherrypy.wsgiserver'],
        scripts = ['twanager',],
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['selector', 'simplejson', 'BeautifulSoup<=3.0.7a', 'wikklytext'],
        include_package_data = True,
        )




