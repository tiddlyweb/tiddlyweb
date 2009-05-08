
import cgi

from tiddlyweb.filters.select import select_by_attribute, select_relative_attribute, select_parse
from tiddlyweb.filters.sort import sort_by_attribute, sort_parse
from tiddlyweb.filters.limit import limit, limit_parse


class FilterError(Exception):
    """
    An exception to throw when an attempt is made to
    filter on an unavailable attribute.
    """
    pass


FILTER_PARSERS = {
        'select': select_parse,
        'sort':   sort_parse,
        'limit':  limit_parse,
        }


def parse_for_filters(query_string):
    if ';' in query_string:
        strings = query_string.split(';')
    else:
        strings = query_string.split('&')

    filters = []
    leftovers = [] 
    for string in strings:
        query = cgi.parse_qs(string)
        try:
            key, value = query.items()[0]

            try:
                argument = unicode(value[0], 'UTF-8')
            except TypeError:
                argument = value[0]

            func = FILTER_PARSERS[key](argument)
            filters.append(func)
        except(KeyError, IndexError):
            leftovers.append(string)

    leftovers = ';'.join(leftovers)
    return filters, leftovers


def recursive_filter(filters, tiddlers):
    if len(filters) == 0:
        return tiddlers
    filter = filters.pop(0)
    try:
        return recursive_filter(filters, filter(tiddlers))
    except AttributeError, exc:
        raise FilterError('malformed filter: %s' % exc)
