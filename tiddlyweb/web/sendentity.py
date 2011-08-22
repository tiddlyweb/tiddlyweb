"""
Send a bag or recipe out HTTP, first serializing to the correct type.
This consolidates common code for bags and recipes.
"""

from tiddlyweb.serializer import Serializer, NoSerializationError
from tiddlyweb.web.http import HTTP304, HTTP415
from tiddlyweb.web.util import get_serialize_type, entity_etag


def send_entity(environ, start_response, entity):
    """
    Send a bag or recipe out HTTP, first serializing to
    the correct type. If the incoming etag matches, raise
    304.
    """
    etag_string = entity_etag(environ, entity)
    incoming_etag = environ.get('HTTP_IF_NONE_MATCH', None)
    if incoming_etag:
        if incoming_etag == etag_string:
            raise HTTP304(incoming_etag)

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
