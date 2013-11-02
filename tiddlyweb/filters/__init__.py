"""
Overarching handler for TiddlyWeb `filters`_.

.. _filters: http://tiddlyweb.tiddlyspace.com/filter

Filters provide an extensible syntax for limiting any :py:class:`Collection
<tiddlyweb.model.collections.Collection>` by attributes on the entities in
the collection. Though primarily for :py:class:`Tiddlers
<tiddlyweb.model.tiddler.Tiddler>`, :py:class:`Bags
<tiddlyweb.model.bag.Bag>` and :py:class:`Recipes
<tiddlyweb.model.recipe.Recipe>` can be filtered as well.

The basic filters provide for selecting and sorting on attributes of the
entities and for limiting (the number of) entities. These basic types of
filter can be extended with plugins, and the ways attributes are processed
can also be extended.

Filters are parsed from a string that is formatted as a ``CGI`` query string
with parameters and arguments. The parameter is a filter type. Each
filter is processed in sequence: the first processing all the entities
handed to it, the next taking only those that result from the first.

Filters can be extended by adding more parsers to ``FILTER_PARSERS``.
Parsers for existing filter types may be extended as well (see the
documentation for each type).

The call signature for a filter is::

    filter(entities, indexable=indexable, environ=environ)

The attribute and value for which a filter filters is established in
the parsing stage and are set as upvalues of the filter closure that
gets created.

``indexable`` and ``environ`` are optional parameters that in special cases
allow a :py:mod:`select <tiddlyweb.filters.select>` style filter to be
optimized with the use of an index. In the current implementation this is
only done when:

* the select filter is the first filter in a stack of filters passed to
  :py:func:`recursive_filter`
* the entities to be filtered are :py:class:`tiddlers
  <tiddlyweb.model.tiddler.Tiddler>` in the context of a :py:class:`bag
  <tiddlyweb.model.bag.Bag>` (this helps to constrain the index)

When both of the above are true the system looks for a module named by
``tiddlyweb.config['indexer']``, imports it, looks for a function called
``indexy_query``, and passes ``environ`` and information about the bag
and the attribute being selected.

What ``index_query`` does to satisfy the query is up to the module. It
should return a list of tiddlers that have been loaded from the
:py:class:`tiddlyweb.store.Store`.

If for some reason ``index_query`` does not wish to perform the query (e.g.
the index cannot satisfy the query) it may raise ``FilterIndexRefused`` and
the normal filtering process will be performed.

Note that testing should be done to determine if using an index is
of any benefit. In some stores (for example caching stores) traversing
the tiddlers is faster than using an index.
"""

from tiddlyweb.filters.select import select_parse
from tiddlyweb.filters.sort import sort_parse
from tiddlyweb.filters.limit import limit_parse

from tiddlyweb.fixups import parse_qs, unicode


class FilterError(Exception):
    """
    An exception to throw when an attempt is made to filter on an
    unavailable attribute.
    """
    pass


class FilterIndexRefused(FilterError):
    """
    A filter index has refused to satisfy a filter with its index.
    """
    pass


FILTER_PARSERS = {
        'select': select_parse,
        'sort': sort_parse,
        'limit': limit_parse,
}


def parse_for_filters(query_string, environ=None):
    """
    Take a string that looks like a ``CGI`` query string and parse it
    for filters. Return a tuple of a list of filter functions and
    a string of whatever was in the query string that did not result
    in a filter.
    """
    if environ is None:
        environ = {}

    if ';' in query_string:
        strings = query_string.split(';')
    else:
        strings = query_string.split('&')

    filters = []
    leftovers = []
    for string in strings:
        query = parse_qs(string)
        try:
            key, value = list(query.items())[0]

            # We need to adapt to different types from the
            # query_string. It changes per Python version,
            # and per store (because of Python version).
            # Sometimes we will already be unicode here,
            # sometimes not.
            try:
                argument = unicode(value[0], 'UTF-8')
            except TypeError:
                argument = value[0]

            func = FILTER_PARSERS[key](argument)
            filters.append((func, (key, argument), environ))
        except(KeyError, IndexError, ValueError):
            leftovers.append(string)

    leftovers = ';'.join(leftovers)
    return filters, leftovers


def recursive_filter(filters, entities, indexable=False):
    """
    Recursively process the list of ``filters`` found by
    :py:func:`parse_for_filters` against the given list of ``entities``.

    Each next filter processes only those entities that were results of
    the previous filter.

    *Misnamed, early versions were more truly recursive.*
    """
    for filter_command in filters:
        try:
            active_filter, _, environ = filter_command
        except ValueError:
            active_filter = filter_command
            environ = {}
        try:
            entities = active_filter(entities, indexable, environ)
        except FilterIndexRefused as exc:
            entities = active_filter(entities, False, environ)
        except (ValueError, AttributeError) as exc:
            raise FilterError('malformed filter: %s' % exc)
        indexable = False
    return entities
