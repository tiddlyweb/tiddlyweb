"""
See http://tiddlyweb.com/ for more complete information.

TiddlyWeb is a web service and library for managing and manipulating
resources useful in the creation of dynamic wikis. The model of the data
is especially useful for creating custom TiddlyWiki implementations,
where the content of the TiddlyWiki can be saved to the server, and
shared among multiple users.

TiddlyWeb presents an HTTP API for resource management. The API follows,
as possible, RESTful principles to keep the API flexible and scalable.
The URLs for this interface are kept in a file called urls.map found in
the tiddlyweb package. urls.map dispatches web requests at specific URLs
to specific functions in modules in the tiddlyweb.web.handler package.
urls.map may be located in another place by changing the urls_map key in
tiddlywebconfig.py. There are also mechanisms for overriding storage
(see tiddlyweb.store), serialization (see tiddlyweb.serializer) and
authentication (see tiddlyweb.web.challenger and
tiddlyweb.web.extractor) systems. There are also system_plugins and
twanager_plugins for further extensibility.

The primary resources presented by the server are Recipes, Bags and
Tiddlers. See the tiddlyweb.model package.

TiddlyWeb includes twanager, a command line tool for doing a variety
of TiddlyWeb activities. Run twanager without arguments for a list
of commands.

See the documentation for other modules and packages within tiddlyweb
for additional details. Visit http://tiddlyweb.com/ for links to
additional information.
"""

__version__ = '1.2.55'
__author__ = 'Chris Dent (cdent@peermore.com)'
__copyright__ = 'Copyright UnaMesa Association 2008-2011'
__contributors__ = ['Frederik Dohr', 'Zac Bir', 'Jeremy Ruston']
__license__ = 'BSD'
