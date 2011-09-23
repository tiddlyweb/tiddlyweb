"""
Common code used for listing bags and recipes.
"""
from tiddlyweb.filters import recursive_filter, FilterError
from tiddlyweb.model.collections import Container
from tiddlyweb.model.policy import UserRequiredError, ForbiddenError
from tiddlyweb.serializer import NoSerializationError
from tiddlyweb.web.http import HTTP304, HTTP400, HTTP415
from tiddlyweb.util import sha


def list_entities(environ, start_response, mime_type, store_list,
        serializer_list):
    """
    Get a list of all the bags or recipes the current user can read.
    """
    filters = environ['tiddlyweb.filters']
    try:
        kept_entities = _filter_readable(environ, store_list(), filters)
    except FilterError, exc:
        raise HTTP400(exc)

    etag_string = '"%s:%s"' % (kept_entities.hexdigest(),
            sha(mime_type).hexdigest())
    incoming_etag = environ.get('HTTP_IF_NONE_MATCH', None)
    if incoming_etag:
        if incoming_etag == etag_string:
            raise HTTP304(incoming_etag)

    start_response("200 OK", [('Content-Type', mime_type),
                ('Vary', 'Accept'),
                ('Cache-Control', 'no-cache'),
                ('Etag', etag_string)])

    try:
        output = serializer_list(kept_entities)
    except NoSerializationError:
        raise HTTP415('Content type not supported: %s' % mime_type)

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
