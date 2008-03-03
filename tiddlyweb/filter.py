
"""
Utilities for filtering tiddlers by the various tiddler
filtering strategies. We translate a filter string
into a series of instructions (functions) which can
be layered.

You'll note some repetition here, which suggests that
there will be some room for meta something or other
coming in here.
"""

import re

def compose_from_string(filter_string):
    """
    Borrowed from filterTiddlers in the TiddlyWiki javascript.
    This feels very not pythonic.

    Also it does not check its own syntax or throw errors
    on bad syntax, which we might enjoy.
    """
    filters = []
    filter_matcher = re.compile(
            r'([^ \[\]]+)|(?:\[([!-]?[ \w]+)\[([^\]]+)\]\])|(?:\[\[([^\]]+)\]\])',
            re.MULTILINE)
    for match in filter_matcher.finditer(filter_string):
        if match.group(1) or match.group(4):
            if match.group(1):
                title = match.group(1)
            else:
                title = match.group(4)
            if title.startswith('!'):
                filters.append([negate(by_title), title.lstrip('!')])
            elif title.startswith('-'):
                filters.append([remove(by_title), title.lstrip('-')])
            else:
                filters.append([by_title, title])
        elif match.group(2):
            flag = match.group(2)
            argument = match.group(3)
            if flag == 'tag':
                filters.append([by_tag, argument])
            elif flag == '!tag':
                filters.append([negate(by_tag), argument])
            elif flag == '-tag':
                filters.append([remove(by_tag), argument])
    return filters

def by_title(title, tiddlers):
    """
    Return those tiddlers that match title.
    """

    return [tiddler for tiddler in tiddlers if tiddler.title == title]

def by_tag(tag, tiddlers):
    """
    Return those tiddlers that have tag tag.
    """

    return [tiddler for tiddler in tiddlers if tag in tiddler.tags]

def by_composition(filters, tiddlers):
    """
    Build a list of tiddlers from a list of filters.
    We are adding to a list, not winnowing a list.
    """

# special case no filters to return all tiddlers
    if len(filters) == 0 or filters == None:
        return tiddlers

    found_tiddlers = {}
    for filter in filters:
        if filter[0].__dict__.has_key('removal'):
            for tiddler in filter[0](filter[1], found_tiddlers.values()):
                if tiddler.title in found_tiddlers:
                    del found_tiddlers[tiddler.title]
        else:
            for tiddler in filter[0](filter[1], tiddlers):
                found_tiddlers[tiddler.title] = tiddler

    return found_tiddlers.values()

def remove(filter):
    """
    Return a function which returns filter.

    Removal only operates during composition. That is
    there must already be a built up list of tiddlers
    from which removal will be done.
    """
    def remove_filter(argument, tiddlers):
        return filter(argument, tiddlers)

    remove_filter.removal = 1

    return remove_filter

def negate(filter):
    """
    Return a function which returns filter, negated.
    That is, the reults are the opposite of what they
    would be if filter were called by itself.
    """
    def negated_filter(argument, tiddlers):
        filtered_tiddlers = filter(argument, tiddlers)
        return [tiddler for tiddler in tiddlers if tiddler not in filtered_tiddlers]

    return negated_filter

def filter_bag(bag, filter, filterargs=None):
    """
    Return the list of tiddlers resulting from filtering
    bag by filter. filter may be a filter function, in 
    which case filterags may need to be set, or may be
    a filter string.
    """
    if callable(filter):
        return filter(filterargs, bag.list_tiddlers())
    else:
        filters = compose_from_string(filter)
        return by_composition(filters, bag.list_tiddlers())

