"""
For more complete information also see:

* http://tiddlyweb.com/
* http://tiddlyweb.tiddlyspace.com/
* http://tiddlyweb.readthedocs.org/

TiddlyWeb is a web service and library for managing and manipulating
resources useful in the creation of dynamic wiki-like collections of
content and functionality. The model of the data was originally designed
for creating custom TiddlyWiki implementations, where the content of
the TiddlyWiki can be saved to the server, and shared among multiple users.

TiddlyWeb presents an ``HTTP API`` for resource management. The API follows,
as possible, RESTful principles to keep the API flexible and scalable.
The URLs for this interface are kept in a file called ``urls.map`` found in
the tiddlyweb package. ``urls.map`` dispatches web requests at specific URLs
to specific functions in modules in the :mod:`tiddlyweb.web.handler` package.
``urls.map`` may be located in another place by changing the ``urls_map`` key
in `tiddlywebconfig.py`_. There are also mechanisms for overriding storage
(see :mod:`tiddlyweb.store`), serialization (see :mod:`tiddlyweb.serializer`)
and authentication (see :mod:`tiddlyweb.web.challenger` and
:mod:`tiddlyweb.web.extractor`) systems. There are also ``system_plugins`` and
``twanager_plugins`` for further extensibility.

.. _tiddlywebconfig.py: http://tiddlyweb.tiddlyspace.com/tiddlywebconfig.py

The primary resources presented by the server are `Recipes`_, `Bags`_ and
`Tiddlers`_. See the :mod:`tiddlyweb.model` package.

.. _Recipes: http://tiddlyweb.tiddlyspace.com/recipe
.. _Bags: http://tiddlyweb.tiddlyspace.com/bag
.. _Tiddlers: http://tiddlyweb.tiddlyspace.com/tiddler

TiddlyWeb includes `twanager`_, a command line tool for doing a variety
of TiddlyWeb activities. Run ``twanager`` without arguments for a list
of commands.

.. _twanager: http://tiddlyweb.tiddlyspace.com/twanager

See the documentation for other modules and packages within tiddlyweb
for additional details.
"""

__version__ = '1.4.17'
__author__ = 'Chris Dent (cdent@peermore.com)'
__copyright__ = 'Copyright UnaMesa Association 2008-2013'
__contributors__ = ['Frederik Dohr', 'Zac Bir', 'Jeremy Ruston']
__license__ = 'BSD'
