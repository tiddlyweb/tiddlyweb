"""
Send a :py:class:`bag <tiddlyweb.model.bag.Bag>` or :py:class:`recipe
<tiddlyweb.model.recipe.Recipe>` out over HTTP, first :py:class:`serializing
<tiddlyweb.serializer.Serializer>` to the correct type.

This consolidates common code for bags and recipes.
"""

from httpexceptor import HTTP415

from tiddlyweb.serializer import Serializer, NoSerializationError
from tiddlyweb.web.util import (get_serialize_type, entity_etag,
        check_incoming_etag)

from tiddlyweb.fixups import basestring


def send_entity(environ, start_response, entity):
    """
    Send a :py:class:`bag <tiddlyweb.model.bag.Bag>` or :py:class:`recipe
    <tiddlyweb.model.recipe.Recipe>` out over HTTP, first
    :py:class:`serializing <tiddlyweb.serializer.Serializer>` to
    the correct type. If an incoming ``Etag`` validates, raise a
    ``304`` response.
    """
    etag_string = entity_etag(environ, entity)
    check_incoming_etag(environ, etag_string)

    try:
        serialize_type, mime_type = get_serialize_type(environ)
        serializer = Serializer(serialize_type, environ)
        serializer.object = entity
        content = serializer.to_string()
    except NoSerializationError:
        raise HTTP415('Content type %s not supported' % mime_type)

    start_response("200 OK",
            [('Content-Type', mime_type),
                ('Cache-Control', 'no-cache'),
                ('ETag', etag_string),
                ('Vary', 'Accept')])

    if isinstance(content, basestring):
        return [content]
    else:
        return content
