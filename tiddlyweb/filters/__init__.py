
from tiddlyweb.filters.select import select_by_attribute, select_relative_attribute
from tiddlyweb.filters.sort import sort_by_attribute
from tiddlyweb.filters.limit import limit


def select_parse(command):
    attribute, args = command.split(':', 1)

    if args.startswith('!'):
        args = args.replace('!', '', 1)
        def selector(tiddlers):
            return select_by_attribute(attribute, args, tiddlers, negate=True)
    elif args.startswith('<'):
        args = args.replace('<', '', 1)
        def selector(tiddlers):
            return select_relative_attribute(attribute, args, tiddlers, lesser=True)
    elif args.startswith('>'):
        args = args.replace('>', '', 1)
        def selector(tiddlers):
            return select_relative_attribute(attribute, args, tiddlers, greater=True)
    else:
        def selector(tiddlers):
            return select_by_attribute(attribute, args, tiddlers)

    return selector


def sort_parse(attribute):
    attribute

    if attribute.startswith('-'):
        attribute = attribute.replace('-', '', 1)
        def sorter(tiddlers):
            return sort_by_attribute(attribute, tiddlers, reverse=True)
    else:
        def sorter(tiddlers):
            return sort_by_attribute(attribute, tiddlers)

    return sorter


def limit_parse(count='0'):
    index = '0'
    if ',' in count:
        index, count = count.split(',', 1)
    index = int(index)
    count = int(count)
    def limiter(tiddlers):
        return limit(tiddlers, index=index, count=count)

    return limiter


FILTER_PARSERS = {
        'select': select_parse,
        'sort':   sort_parse,
        'limit':  limit_parse,
        }

def recursive_filter(filters, tiddlers):
    if len(filters) == 0:
        return tiddlers
    filter = filters.pop(0)
    return recursive_filter(filters, filter(tiddlers))
