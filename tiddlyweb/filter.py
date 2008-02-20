
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
            r'([^ \[\]]+)|(?:\[(-?[ \w]+)\[([^\]]+)\]\])|(?:\[\[([^\]]+)\]\])',
            re.MULTILINE)
    for match in filter_matcher.finditer(filter_string):
        if match.group(1) or match.group(4):
            if match.group(1):
                title = match.group(1)
            else:
                title = match.group(4)
            filters.append([by_name, title])
        elif match.group(2):
            flag = match.group(2)
            argument = match.group(3)
            if flag == 'tag':
                filters.append([by_tag, argument])
            elif flag == '-tag':
                filters.append([negate(by_tag), argument])
    return filters

def by_name(name, tiddlers):
    """
    Return those tiddlers that match name.
    """

    return [tiddler for tiddler in tiddlers if tiddler['name'] == name]

def by_tag(tag, tiddlers):
    """
    Return those tiddlers that have tag tag.
    """

    return [tiddler for tiddler in tiddlers if tag in tiddler['tags']]

def by_composition(filters, tiddlers):
    """
    Build a list of tiddlers from a list of filters.
    We are adding to a list, not winnowing a list.
    """

    found_tiddlers = {}
    for filter in filters:
        for tiddler in filter[0](filter[1], tiddlers):
            found_tiddlers[tiddler['name']] = tiddler

    return found_tiddlers.values()

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

