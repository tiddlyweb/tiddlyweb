"""
Limit a group of tiddlers using a syntax similar
to SQL Limit:

    limit=<index>,<count>
    limit=<count>
"""


def limit_parse(count='0'):
    """
    Parse the argument of a limit filter
    for a count and index argument, return
    a function which does the limiting.

    Exceptions while parsing are passed
    up the stack.
    """
    index = '0'
    if ',' in count:
        index, count = count.split(',', 1)
    index = int(index)
    count = int(count)

    def limiter(tiddlers, indexable=False, environ=None):
        return limit(tiddlers, index=index, count=count)

    return limiter


def limit(tiddlers, count=0, index=0):
    """
    Make a slice of a list of tiddlers based
    on a count and index.
    """
    # The following optimizes the common case of taking the short top
    # of a long list of tiddlers. The other option is to switch to a
    # list first and then take a slice as follows:
    # tiddlers = list(tiddlers)
    # return (tiddler for tiddler in tiddlers[index:index+count])
    for enum_index, tiddler in enumerate(tiddlers):
        if enum_index < index:
            continue
        if enum_index > (index + count - 1):
            return
        yield tiddler
    return
