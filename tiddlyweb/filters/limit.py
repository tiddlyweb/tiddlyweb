"""
Limit a group of entities using a syntax similar to SQL Limit:

    limit=<index>,<count>
    limit=<count>
"""

import itertools


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

    def limiter(entities, indexable=False, environ=None):
        return limit(entities, index=index, count=count)

    return limiter


def limit(entities, count=0, index=0):
    """
    Make a slice of a list of entities based
    on a count and index.
    """

    return itertools.islice(entities, index, index + count)
