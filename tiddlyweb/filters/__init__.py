"""
Overarching handler for TiddlyWeb filters.

This is the second iteration of filters for TiddlyWeb.
The first version was based on TiddlyWiki filters but
this was found to be not entirely well suited to the
HTTP situation in which TiddlyWeb finds itself, nor
was it particularly easy to extend in a way that was
simple, clear and powerful.

This new style hopes to be some of those things.

Filters are parsed from a string that is formatted
as a CGI query string with parameters and arguments.
The parameter is a filter type. Each filter is processed
in sequence: the first processing all the tiddlers
handed to it, the next taking only those that result
from the first.

Filters can be extended by adding more parsers to
FILTER_PARSERS. Parsers for existing filter types
may be extended as well (see the documentation for
each type).

The call signature for a filter is:

    filter(tiddlers, indexable=indexable, environ=environ)

The attribute and value for which a filter filters is
established in the parsing stage and set as upvalues
of the filter closure that gets created.

indexable and environ are optional parameters that
in special cases allow a select style filter to be
optimized with the use of an index. In the current
implementation this is only done when:

 * the select filter is the first filter in a stack
   of filters passed to recursive_filter
 * the list of tiddlers to be filtered is a standard
   bag (wherein all the tiddlers in the bag "live"
   in that bag)

When both of the above are true the system looks for a
module named by tiddlyweb.config['indexer'], imports it,
looks for a function called indexy_query, and passes
environ and information about the bag and the attribute
being selected.

What index_query does to satify the query is up to the
module. It should return a list of tiddlers that have
been loaded from tiddlyweb.store.

If for some reason index_query does not wish to perform
the query (e.g. the index cannot satisfy the query) it
may raise FilterIndexRefused and the normal filtering
process will be performed.
"""

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from tiddlyweb.filters.select import select_by_attribute, \
        select_relative_attribute, select_parse
from tiddlyweb.filters.sort import sort_by_attribute, sort_parse
from tiddlyweb.filters.limit import limit, limit_parse


class FilterError(Exception):
    """
    An exception to throw when an attempt is made to
    filter on an unavailable attribute.
    """
    pass


class FilterIndexRefused(FilterError):
    """
    A filter index has refused to satisfy a filter
    with its index.
    """
    pass


FILTER_PARSERS = {
        'select': select_parse,
        'sort': sort_parse,
        'limit': limit_parse,
        }


def parse_for_filters(query_string, environ=None):
    """
    Take a string that looks like a CGI query
    string and parse if for filters. Return
    a tuple of a list of filter functions and
    a string of whatever was in the query string that
    did not result in a filter.
    """
    if environ == None:
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
            key, value = query.items()[0]

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


def recursive_filter(filters, tiddlers, indexable=False):
    """
    Recursively process the list of filters found
    by parse_for_filters against the given list
    of tiddlers.

    Each next filter processes only those tiddlers
    that were results of the previous filter.
    """
    if len(filters) == 0:
        return (tiddler for tiddler in tiddlers)
    current_filter = filters.pop(0)
    try:
        active_filter, args, environ = current_filter
    except ValueError:
        active_filter = current_filter
        environ = {}
    try:
        return recursive_filter(filters, active_filter(tiddlers, indexable,
            environ), indexable=False)
    except FilterIndexRefused, exc:
        filters.insert(0, current_filter)
        return recursive_filter(filters, tiddlers, indexable=False)
    except AttributeError, exc:
        raise FilterError('malformed filter: %s' % exc)
