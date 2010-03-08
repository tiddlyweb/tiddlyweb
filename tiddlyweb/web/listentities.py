"""
Handle common code used for listing bags and recipes.
"""
from tiddlyweb.model.policy import UserRequiredError, ForbiddenError
from tiddlyweb.serializer import NoSerializationError
from tiddlyweb.web.http import HTTP415


def list_entities(environ, start_response, mime_type, store_list,
        serializer_list):
    """
    Get a list of all the bags or recipes the current user can read.
    """
    store = environ['tiddlyweb.store']
    entities = store_list()
    kept_entities = []
    for entity in entities:
        try:
            entity.skinny = True
            entity = store.get(entity)
            try:
                delattr(entity, 'skinny')
            except AttributeError:
                pass
            entity.policy.allows(environ['tiddlyweb.usersign'], 'read')
            kept_entities.append(entity)
        except(UserRequiredError, ForbiddenError):
            pass

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
