"""
Filter routines for selecting some entities,
usually tiddlers, from a collection of entities,
usually by an attribute of the tiddlers.

The syntax is:

    select=attribute:value
    select=attribute:!value
    select=attribute:>value
    select=attribute:<value

ATTRIBUTE_SELECTOR is checked for a function which returns
true or false for whether the provide value matches for
the entity being tested. The default case is lower case
string equality. Other functions may be provided by
plugins and other extensions. Attributes may be virtual,
i.e. not real attributes on entity. For example we can
check for the presence of a tag in a tiddlers tags attribute
with

    select=tag:tagvalue

An attribute function takes an entity, an attribute name and
a value, may do anything it wants with it, and must return
True or False.

'!' negates a selection, getting all those entities that
don't match.

'>' gets those entities that sort greater than the value.

'<' gets those entities that sort less than the value.

When doing sorting ATTRIBUTE_SORT_KEY is consulted to
canonicalize the value. See tiddlyweb.filters.sort.
"""

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
            return select_by_attribute(attribute, args, entities, negate=True)

    elif args.startswith('<'):
        args = args.replace('<', '', 1)

        def selector(entities, indexable=False, environ=None):
            return select_relative_attribute(attribute, args, entities,
                    lesser=True)

    elif args.startswith('>'):
        args = args.replace('>', '', 1)

        def selector(entities, indexable=False, environ=None):
            return select_relative_attribute(attribute, args, entities,
                    greater=True)

    else:

        def selector(entities, indexable=False, environ=None):
            if environ == None:
                environ = {}
            return select_by_attribute(attribute, args, entities,
                    indexable=indexable, environ=environ)

    return selector


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
    return value.lower() in entity.text.lower()


ATTRIBUTE_SELECTOR = {
        'tag': tag_in_tags,
        'text': text_in_text,
        'field': field_in_fields,
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
        if negate:
            for entity in entities:
                if not select(entity, attribute, value):
                    yield entity
        else:
            for entity in entities:
                if select(entity, attribute, value):
                    yield entity
    return


def select_relative_attribute(attribute, value, entities,
        greater=False, lesser=False):
    """
    Select entities that sort greater or less than the provided value
    for the provided attribute.
    """

    def normalize_value(value):
        """lower case the value if it is a string"""
        try:
            return value.lower()
        except AttributeError:
            return value

    func = ATTRIBUTE_SORT_KEY.get(attribute, normalize_value)

    if greater:
        for entity in entities:
            if hasattr(entity, 'fields'):
                if func(getattr(entity, attribute, entity.fields.get(
                    attribute, None))) > func(value):
                    yield entity
            else:
                if func(getattr(entity, attribute, None)) > func(value):
                    yield entity
    elif lesser:
        for entity in entities:
            if hasattr(entity, 'fields'):
                if func(getattr(entity, attribute, entity.fields.get(
                    attribute, None))) < func(value):
                    yield entity
            else:
                if func(getattr(entity, attribute, None)) < func(value):
                    yield entity
    else:
        for entity in entities:
            yield entity
