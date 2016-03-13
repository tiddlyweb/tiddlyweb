.. image:: https://secure.travis-ci.org/tiddlyweb/tiddlyweb.png
    :target: http://travis-ci.org/tiddlyweb/tiddlyweb
    :alt: build status
.. image:: https://pypip.in/v/tiddlyweb/badge.png
    :target: https://pypi.python.org/pypi/tiddlyweb
    :alt: Package Version
.. image:: https://pypip.in/d/tiddlyweb/badge.png
    :target: https://pypi.python.org/pypi/tiddlyweb
    :alt: Package Downloads

* TiddlyWeb Home Site: http://tiddlyweb.com/
* TiddlyWeb Git Repo: http://github.com/tiddlyweb/tiddlyweb

For additional installation instructions see http://docs.tiddlyweb.com/

**With the 2.0.0 release of TiddlyWeb versions 2.7 and 3.3 and beyond
of Python are supported. Earlier versions may work but are not explicitly
tested.** Note that ``tiddlywebwiki`` and most plugins have not yet been
ported to work with Python 3 but will work with 2.7. Work to bring them up
to date is in progress.

Introduction
============

TiddlyWeb is an open source HTTP API for storing and accessing flexible
and composable microcontent. It is also a toolkit for tiddlers on the web.
Tiddlers are small chunks of optionally structured content
with their own URI. The concept comes from `TiddlyWiki <http://tiddlywiki.com>`_.
TiddlyWeb can provide the basis of a `server side for TiddlyWiki
<http://pypi.python.org/pypi/tiddlywebwiki>`_. TiddlyWeb provides:

* an abstract model (with default implementations) for:

  * authentication and authorization
  * entity storage 
  * entity and collection serialization

* a straightforward extension model via plugins
* an implementation of authenticated recipes and bags allowing
  access to dynamically created and filtered collections of tiddlers
* a clean and pragmatic HTTP API

The system is designed so that parts that are not optimal for a
particular installation can be easily improved or swapped out via
plugins.

While TiddlyWeb was initially designed as a TiddlyWiki server-side
it can also be used as a generic data store and platform. The platform
builds on concepts learned from TiddlyWiki, primarily the concept of
the tiddler: a small chunk of data used to build up a greater whole.

TiddlyWeb includes a command line tool called ``twanager``. Run ``twanager``
without arguments for a list of available commands.

Installation
============

The easiest way to install TiddlyWeb and all its dependencies is by
using `pip <http://pip.openplans.org/>`_ to install it from `PyPI
<http://pypi.python.org>`_:::

   pip install -U tiddlyweb

If you wish to use TiddlyWeb as a server-side for TiddlyWiki to generate
a multi-user TiddlyWiki system, you will also need `tiddlywebwiki
<http://pypi.python.org/pypi/tiddlywebwiki>`_. This too can be installed
via pip. Installing tiddlywebwiki will install tiddlyweb for you:::

   pip install -U tiddlywebwiki

Or you can install by hand, you will need the following requirements:

* Python 2.7 or Python 3.3. Earlier versions may work but are neither
  tested nor recommended.
* selector: http://lukearno.com/projects/selector/
* simplejson: http://undefined.org/python/#simplejson
* html5lib (for sanitizing input which may be rendered as HTML):
  http://code.google.com/p/html5lib/
* httpexceptor: http://pypi.python.org/pypi/httpexceptor

Building
=============

Tests are run using PyTest:

   make test

Coverage support with:

https://pypi.python.org/pypi/coverage
https://pypi.python.org/pypi/pytest-cov

Miscellaneous
=============

See http://pypi.python.org/pypi?%3Aaction=search&term=tiddlywebplugins
for plugins that TiddlyWeb can use with itself.

If you have questions or contributions on making TiddlyWeb work
for you, please post to the TiddlyWeb group at google groups:

  http://groups.google.com/group/tiddlyweb

or contact the primary author, Chris Dent <cdent@peermore.com>.

Please report bugs and issues at the github issue tracker:

  https://github.com/tiddlyweb/tiddlyweb/issues

There are a few tools that make exploring TiddlyWeb a bit easier:

* Python API explorer: ``twanager interact`` (once in type ``locals().keys()``)
* HTTP API quick ref: http://docs.tiddlyweb.com/HTTP%20API

License
=======
TiddlyWeb is released under the BSD License and is copyright
2008-2016 UnaMesa Association.
