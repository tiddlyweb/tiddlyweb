"""
Handle common code used for listing bags and recipes.
"""
from tiddlyweb.filters import recursive_filter, FilterError
from tiddlyweb.model.collections import Container
from tiddlyweb.model.policy import UserRequiredError, ForbiddenError
from tiddlyweb.serializer import NoSerializationError
from tiddlyweb.web.http import HTTP415, HTTP400
from tiddlyweb.util import sha


def list_entities(environ, start_response, mime_type, store_list,
        serializer_list):
    """
    Get a list of all the bags or recipes the current user can read.
    """
    filters = environ['tiddlyweb.filters']
    username = environ['tiddlyweb.usersign']['name']
    try:
        kept_entities = _filter_readable(environ, store_list(), filters)
    except FilterError, exc:
        raise HTTP400(exc)

    etag_string = '"%s:%s"' % (kept_entities.hexdigest(),
            sha('%s:%s' % (username, mime_type)).hexdigest())
    start_response("200 OK", [('Content-Type', mime_type),
                ('Vary', 'Accept'),
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
    kept_entities = Container()
    for entity in recursive_filter(filters, entities):
        try:
            if hasattr(entity, 'store') and entity.store:
                pass
            else:
                entity = store.get(entity)
            entity.policy.allows(environ['tiddlyweb.usersign'], 'read')
            kept_entities.add(entity)
        except(UserRequiredError, ForbiddenError):
            pass
    return kept_entities
