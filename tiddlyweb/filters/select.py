"""
Filter routines for selecting some tiddlers from
a collection of tiddlers, usually by an attribute
of the tiddlers.

The syntax is:

    select=attribute:value
    select=attribute:!value
    select=attribute:>value
    select=attribute:<value

ATTRIBUTE_SELECTOR is checked for a function which returns
true or false for whether the provide value matches for
the tiddler being tested. The default case is lower case
string equality. Other functions may be provided by
plugins and other extensions. Attributes may be virtual,
i.e. not real attributes on tiddlers. For example we can
check for the presence of a tag in the tags attribute with

    select=tag:tagvalue

An attribute function takes a tiddler, an attribute name and
a value, may do anything it wants with it, and must return
True or False.

'!' negates a selection, getting all those tiddlers that
don't match.

'>' gets those tiddlers that sort greater than the value.

'<' gets those tiddlers that sort less than the value.

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

        def selector(tiddlers, indexable=False, environ=None):
            return select_by_attribute(attribute, args, tiddlers, negate=True)

    elif args.startswith('<'):
        args = args.replace('<', '', 1)

        def selector(tiddlers, indexable=False, environ=None):
            return select_relative_attribute(attribute, args, tiddlers,
                    lesser=True)

    elif args.startswith('>'):
        args = args.replace('>', '', 1)

        def selector(tiddlers, indexable=False, environ=None):
            return select_relative_attribute(attribute, args, tiddlers,
                    greater=True)

    else:

        def selector(tiddlers, indexable=False, environ=None):
            if environ == None:
                environ = {}
            return select_by_attribute(attribute, args, tiddlers,
                    indexable=indexable, environ=environ)

    return selector


def field_in_fields(tiddler, attribute, value):
    """
    Return true if the tiddler has the named field.
    """
    return value in tiddler.fields


def tag_in_tags(tiddler, attribute, value):
    """
    Return true if the provide tiddler has
    a tag of value in its tag list.
    """
    return value in tiddler.tags


def text_in_text(tiddler, attribute, value):
    """
    Return true if the provided tiddler has
    the string provided in value in its
    text attribute.
    """
    return value.lower() in tiddler.text.lower()


ATTRIBUTE_SELECTOR = {
        'tag': tag_in_tags,
        'text': text_in_text,
        'field': field_in_fields,
        }


def default_func(tiddler, attribute, value):
    """
    Look in the tiddler for an attribute with the
    provided value. First proper attributes are
    checked, then extended fields. If neither of
    these are present, return False.
    """
    try:
        return getattr(tiddler, attribute) == value
    except AttributeError:
        try:
            return tiddler.fields[attribute] == value
        except KeyError:
            return False


def select_by_attribute(attribute, value, tiddlers, negate=False,
        indexable=None, environ=None):
    """
    Select tiddlers where value of attribute matches the provide value.

    If negate is true, get those that don't match.
    """
    if environ == None:
        environ = {}

    if indexable:
        indexer = environ.get('tiddlyweb.config', {}).get('indexer', None)
        if indexer:
            # If there is an exception, just let it raise.
            imported_module = __import__(indexer, {}, {}, ['index_query'])
            # dict keys may not be unicode
            kwords = {str(attribute): value, 'bag': indexable.name}
            return imported_module.index_query(environ, **kwords)

    select = ATTRIBUTE_SELECTOR.get(attribute, default_func)
    if negate:
        return (tiddler for tiddler in tiddlers if not
                select(tiddler, attribute, value))
    else:
        return (tiddler for tiddler in tiddlers if
                select(tiddler, attribute, value))


def select_relative_attribute(attribute, value, tiddlers,
        greater=False, lesser=False):
    """
    Select tiddlers that sort greater or less than the provided value
    for the provided attribute.
    """

    def normalize_value(value):
        try:
            return value.lower()
        except AttributeError:
            return value

    func = ATTRIBUTE_SORT_KEY.get(attribute, normalize_value)

    if greater:
        return (tiddler for tiddler in tiddlers if
                func(getattr(tiddler, attribute, tiddler.fields.get(
                    attribute, None))) > func(value))
    elif lesser:
        return (tiddler for tiddler in tiddlers if
                func(getattr(tiddler, attribute, tiddler.fields.get(
                    attribute, None))) < func(value))
    else:
        return (tiddler for tiddler in tiddlers)
