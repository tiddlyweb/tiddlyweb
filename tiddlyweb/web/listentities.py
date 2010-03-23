"""
Handle common code used for listing bags and recipes.
"""
from tiddlyweb.model.policy import UserRequiredError, ForbiddenError
from tiddlyweb.serializer import NoSerializationError
from tiddlyweb.web.http import HTTP415
from tiddlyweb.filters import recursive_filter


def list_entities(environ, start_response, mime_type, store_list,
        serializer_list):
    """
    Get a list of all the bags or recipes the current user can read.
    """
    store = environ['tiddlyweb.store']
    entities = store_list()
    filters = environ['tiddlyweb.filters']
    kept_entities = _filter_readable(environ, entities, filters)

    start_response("200 OK", [('Content-Type', mime_type),
                ('Vary', 'Accept')])

    try:
        output = serializer_list(kept_entities)
    except NoSerializationError:
        raise HTTP415('Content type not supported: %s' % mime_type)

    if isinstance(output, basestring):
        return [output]
    else:
        return output


def _filter_readable(environ, entities, filters):
    store = environ['tiddlyweb.store']
    for entity in recursive_filter(filters, entities):
        try:
            if hasattr(entity, 'store') and entity.store:
                pass
            else:
                entity = store.get(entity)
            entity.policy.allows(environ['tiddlyweb.usersign'], 'read')
            yield entity
        except(UserRequiredError, ForbiddenError):
            pass
    return
