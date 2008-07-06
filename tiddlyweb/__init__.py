"""
TiddlyWeb is a web service for managing and manipulating
resources useful in the creation of dynamic wikis. The
model of the data is especially useful for creating 
custom TiddlyWiki implementation, where the content of the
TiddlyWiki can be saved to the server, and shared among
multiple users.

TiddlyWeb presents a REST API for the management of the 
resources. The URLs for this interface are kept in a
file called urls.map found in the same directory from
which a TiddlyWeb server is started. urls.map dispatches
web requests at specific URLs to specific functions
in modules in the tiddlyweb.web package.

The primary resources presented by the server are Recipes,
Bags and Tiddlers.
"""
