"""
TiddlyWeb is a web service for managing and manipulating
resources useful in the creation of dynamic wikis. The
model of the data is especially useful for creating
custom TiddlyWiki implementations, where the content of the
TiddlyWiki can be saved to the server, and shared among
multiple users.

TiddlyWeb presents a REST API for the management of the
resources. The URLs for this interface are kept in a
file called urls.map found in the tiddlyweb package.
urls.map dispatches web requests at specific URLs to
specific functions in modules in the tiddlyweb.web
package. urls.map may be located in another place by
changing the urls_map key in tiddlywebconfig. There
are also mechanisms for overriding storage (see
tiddlyweb.store), serialization (see tiddlyweb.serializer)
and authentication (see tiddlyweb.web.challenger and
tiddlyweb.web.extractor) systems. There are also
system_plugins and twanager_plugins for further
extensibility.

The primary resources presented by the server are Recipes,
Bags and Tiddlers. See the tiddlyweb.model package.
"""
__version__ = '0.9.30'
