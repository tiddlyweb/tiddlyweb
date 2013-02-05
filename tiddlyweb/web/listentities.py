"""
Common code used for listing bags and recipes.
"""

from httpexceptor import HTTP400, HTTP415

from tiddlyweb.filters import recursive_filter, FilterError
from tiddlyweb.model.collections import Container
from tiddlyweb.model.policy import UserRequiredError, ForbiddenError
from tiddlyweb.serializer import Serializer, NoSerializationError
from tiddlyweb.util import sha
from tiddlyweb.web.util import get_serialize_type, check_incoming_etag


def list_entities(environ, start_response, method_name,
        store_list=None, serializer_list=None):
    """
    Get a list of all the bags or recipes the current user can read.
    """
    store = environ['tiddlyweb.store']
    serialize_type, mime_type = get_serialize_type(environ, collection=True)
    serializer = Serializer(serialize_type, environ)
    filters = environ['tiddlyweb.filters']
    if method_name:
        if not store_list:
            store_list = getattr(store, method_name)
        if not serializer_list:
            serializer_list = getattr(serializer, method_name)

    try:
        kept_entities = _filter_readable(environ, store_list(), filters)
    except FilterError, exc:
        raise HTTP400(exc)

    etag_string = '"%s:%s"' % (kept_entities.hexdigest(),
            sha(mime_type).hexdigest())
    check_incoming_etag(environ, etag_string)

    try:
        output = serializer_list(kept_entities)
    except NoSerializationError:
        raise HTTP415('Content type not supported: %s' % mime_type)

    start_response("200 OK", [('Content-Type', mime_type),
                ('Vary', 'Accept'),
                ('Cache-Control', 'no-cache'),
                ('Etag', etag_string)])

    if isinstance(output, basestring):
        return [output]
    else:
        return output


def _filter_readable(environ, entities, filters):
    """
    Traverse entities to get those that are readable
    and those that pass the filter.

    XXX: There is a bug here, depending on how
    filters are to be interpreted: If limit is used
    it is being calculated before the readability
    of the entities is checked.
    """
    store = environ['tiddlyweb.store']

    def _load(entities):
        for entity in entities:
            if hasattr(entity, 'store') and entity.store:
                yield entity
            else:
                entity = store.get(entity)
                yield entity

    kept_entities = Container()
    try:
        for entity in recursive_filter(filters, _load(entities)):
            try:
                entity.policy.allows(environ['tiddlyweb.usersign'], 'read')
                kept_entities.add(entity)
            except(UserRequiredError, ForbiddenError):
                pass
    except AttributeError, exc:
        raise FilterError('malformed filter: %s' % exc)
    return kept_entities
