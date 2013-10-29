"""
Convenience routines for presenting the root of the web server.

Here because nowhere else seems right.
"""

from tiddlyweb.serializer import Serializer


ROOT_PAGE = u"""<ul id="root" class="listing">
<li><a href="%s/recipes">recipes</a></li>
<li><a href="%s/bags">bags</a></li>
</ul>"""


def root(environ, start_response):
    """
    Convenience application to provide an entry point at root.
    """

    start_response("200 OK", [('Content-Type', 'text/html; charset=UTF-8')])
    server_prefix = environ['tiddlyweb.config']['server_prefix']
    serializer = Serializer('html', environ)
    environ['tiddlyweb.title'] = 'Home'
    return [serializer.serialization._header(),
            ROOT_PAGE % (server_prefix, server_prefix),
            serializer.serialization._footer()]
