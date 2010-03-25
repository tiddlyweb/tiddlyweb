"""
Send a bag or recipe out HTTP, first serializing to
the correct type.
"""

from tiddlyweb.serializer import Serializer, NoSerializationError
from tiddlyweb.web.http import HTTP415
from tiddlyweb.web.util import get_serialize_type, encode_name
from tiddlyweb.util import sha


def send_entity(environ, start_response, entity):
    """
    Send a bag or recipe out HTTP, first serializing to
    the correct type.
    """
    username = environ['tiddlyweb.usersign']['name']
    try:
        serialize_type, mime_type = get_serialize_type(environ)
        serializer = Serializer(serialize_type, environ)
        serializer.object = entity
        content = serializer.to_string()
    except NoSerializationError:
        raise HTTP415('Content type %s not supported' % mime_type)

    etag_string = '"%s"' % (sha(_entity_etag(entity) +
        encode_name(username) + encode_name(mime_type)).hexdigest())

    start_response("200 OK",
            [('Content-Type', mime_type),
                ('ETag', etag_string),
                ('Vary', 'Accept')])

    if isinstance(content, basestring):
        return [content]
    else:
        return content


def _entity_etag(entity):
    """
    Generate a unique hash from the contents of the entity.
    """
    etag = ''
    etag += entity.name
    for attr in entity.policy.attributes:
        etag += '%s' % getattr(entity.policy, attr)
    try:
        for item in entity:
            etag += '%s' % item
    except TypeError:
        # entity not a iterator
        pass
    return etag.encode('utf-8')
