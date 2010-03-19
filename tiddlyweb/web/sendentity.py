"""
Send a bag or recipe out HTTP, first serializing to
the correct type.
"""

from tiddlyweb.serializer import Serializer, NoSerializationError
from tiddlyweb.web.http import HTTP415
from tiddlyweb.web.util import get_serialize_type


def send_entity(environ, start_response, entity):
    """
    Send a bag or recipe out HTTP, first serializing to
    the correct type.
    """
    try:
        serialize_type, mime_type = get_serialize_type(environ)
        serializer = Serializer(serialize_type, environ)
        serializer.object = entity
        content = serializer.to_string()
    except NoSerializationError:
        raise HTTP415('Content type %s not supported' % mime_type)

    start_response("200 OK",
            [('Content-Type', mime_type),
                ('Vary', 'Accept')])

    if isinstance(content, basestring):
        return [content]
    else:
        return content
