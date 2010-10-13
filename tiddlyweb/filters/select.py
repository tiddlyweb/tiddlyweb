"""
Filter routines for selecting some entities, usually tiddlers, from a
collection of entities, usually by an attribute of the tiddlers.

The syntax is:

    select=attribute:value    # attribute is value
    select=attribute:!value   # attribute is not value
    select=attribute:>value   # attribute is greater than value
    select=attribute:<value   # attribute is less than value

ATTRIBUTE_SELECTOR is checked for a function which returns true or false
for whether the provide value matches for the entity being tested. The
default case is lower case string equality. Other functions may be
provided by plugins and other extensions. Attributes may be virtual,
i.e. not real attributes on entity. For example we can check for the
presence of a tag in a tiddlers tags attribute with

    select=tag:tagvalue

An attribute function takes an entity, an attribute name and a value,
may do anything it wants with it, and must return True or False.

'!' negates a selection, getting all those entities that don't match.

'>' gets those entities that sort greater than the value.

'<' gets those entities that sort less than the value.

When doing sorting ATTRIBUTE_SORT_KEY is consulted to canonicalize the
value. See tiddlyweb.filters.sort.
"""

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import NoTiddlerError
from tiddlyweb.filters.sort import ATTRIBUTE_SORT_KEY


def select_parse(command):
    """
    Parse a select parse command into
    attributes and arguments and return a
    function (for later use) which will do
    the selecting.
    """
    attribute, args = command.split(':', 1)

    if args.startswith('!'):
        args = args.replace('!', '', 1)

        def selector(entities, indexable=False, environ=None):
            return select_by_attribute(attribute, args, entities, negate=True,
                    environ=environ)

    elif args.startswith('<'):
        args = args.replace('<', '', 1)

        def selector(entities, indexable=False, environ=None):
            return select_relative_attribute(attribute, args, entities,
                    lesser=True, environ=environ)

    elif args.startswith('>'):
        args = args.replace('>', '', 1)

        def selector(entities, indexable=False, environ=None):
            return select_relative_attribute(attribute, args, entities,
                    greater=True, environ=environ)

    else:

        def selector(entities, indexable=False, environ=None):
            if environ == None:
                environ = {}
            return select_by_attribute(attribute, args, entities,
                    indexable=indexable, environ=environ)

    return selector


def bag_in_recipe(entity, attribute, value):
    """
    Return true if the named bag is in the recipe.
    """
    bags = [bag for bag, filter in entity.get_recipe()]
    return value in bags


def field_in_fields(entity, attribute, value):
    """
    Return true if the entity has the named field.
    """
    return value in entity.fields


def tag_in_tags(entity, attribute, value):
    """
    Return true if the provided entity has
    a tag of value in its tag list.
    """
    return value in entity.tags


def text_in_text(entity, attribute, value):
    """
    Return true if the provided entity has
    the string provided in value in its
    text attribute.
    """
    try:
        return value.lower() in entity.text.lower()
    except UnicodeDecodeError:
        # Binary tiddler
        return False


ATTRIBUTE_SELECTOR = {
        'tag': tag_in_tags,
        'text': text_in_text,
        'field': field_in_fields,
        'rbag': bag_in_recipe,
        }


def default_func(entity, attribute, value):
    """
    Look in the entity for an attribute with the
    provided value. First proper attributes are
    checked, then extended fields. If neither of
    these are present, return False.
    """
    try:
        return getattr(entity, attribute) == value
    except AttributeError:
        try:
            return entity.fields[attribute] == value
        except (AttributeError, KeyError):
            return False


def select_by_attribute(attribute, value, entities, negate=False,
        indexable=None, environ=None):
    """
    Select entities where value of attribute matches the provide value.

    If negate is true, get those that don't match.
    """
    if environ == None:
        environ = {}

    store = environ.get('tiddlyweb.store', None)
    indexer = environ.get('tiddlyweb.config', {}).get('indexer', None)
    if indexable and indexer:
        # If there is an exception, just let it raise.
        imported_module = __import__(indexer, {}, {}, ['index_query'])
        # dict keys may not be unicode
        kwords = {str(attribute): value, 'bag': indexable.name}
        for tiddler in imported_module.index_query(environ, **kwords):
            yield tiddler
    else:
        select = ATTRIBUTE_SELECTOR.get(attribute, default_func)
        for entity in entities:
            stored_entity = _get_entity(entity, store)
            if negate:
                if not select(stored_entity, attribute, value):
                    yield entity
            else:
                if select(stored_entity, attribute, value):
                    yield entity
    return


def select_relative_attribute(attribute, value, entities,
        greater=False, lesser=False, environ=None):
    """
    Select entities that sort greater or less than the provided value
    for the provided attribute.
    """
    if environ == None:
        environ = {}

    store = environ.get('tiddlyweb.store', None)

    def normalize_value(value):
        """lower case the value if it is a string"""
        try:
            return value.lower()
        except AttributeError:
            return value

    func = ATTRIBUTE_SORT_KEY.get(attribute, normalize_value)

    for entity in entities:
        stored_entity = _get_entity(entity, store)
        if greater:
            if hasattr(stored_entity, 'fields'):
                if func(getattr(stored_entity, attribute, stored_entity.fields.get(
                    attribute, None))) > func(value):
                    yield entity
            else:
                if func(getattr(stored_entity, attribute, None)) > func(value):
                    yield entity
        elif lesser:
            if hasattr(stored_entity, 'fields'):
                if func(getattr(stored_entity, attribute, stored_entity.fields.get(
                    attribute, None))) < func(value):
                    yield entity
            else:
                if func(getattr(stored_entity, attribute, None)) < func(value):
                    yield entity
        else:
            yield entity


def _get_entity(entity, store):
    """
    Load the provided entity from the store if it has not already
    been loaded. In this context only tiddlers will not have been
    loaded already.
    """
    if store and not entity.store:
        try:
            stored_entity = Tiddler(entity.title, entity.bag)
            if entity.revision:
                stored_entity.revision = entity.revision
            stored_entity = store.get(stored_entity)
        except (AttributeError, NoTiddlerError):
            stored_entity = entity
    else:
        stored_entity = entity
    return stored_entity
