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


class FilterError(Exception):
    """
    An exception to throw when an attempt is made to
    filter on an unavailable attribute.
    """
    pass


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
            try:
                filters.append([FILTER_MAP[flag], argument])
            except KeyError:
                filters.append([make_field_filter(flag), argument])
    return filters


def by_title(title, tiddlers):
    """
    Return those tiddlers that match title.
    """
    return [tiddler for tiddler in tiddlers if tiddler.title == title]


def by_since(timespec, tiddlers):
    """
    Return those tiddlers new than the provided timespec.
    """
    if len(timespec) == 12:
        timespec = timespec + '00'
    def newer(tiddler):
        modified = tiddler.modified
        if len(modified) == 12:
            modified = modified + '00'
        return int(modified) >= int(timespec)
    return [tiddler for tiddler in tiddlers if newer(tiddler)]


def by_text(text, tiddlers):
    """
    Return those tiddlers that contain text.
    """
    text = text.lower()
    return [tiddler for tiddler in tiddlers if text in tiddler.text.lower()]


def by_tag(tag, tiddlers):
    """
    Return those tiddlers that have tag tag.
    """
    return [tiddler for tiddler in tiddlers if tag in tiddler.tags]


def by_bag(bag, tiddlers):
    """
    Return those tiddlers that have bag bag.
    """
    return [tiddler for tiddler in tiddlers if tiddler.bag == bag]


def by_composition(filters, tiddlers):
    """
    Build a list of tiddlers from a list of filters.
    We are adding to a list, not winnowing a list.
    """
    # special case no filters to return all tiddlers
    if len(filters) == 0 or filters == None:
        return tiddlers

    # keep the collection unique
    found_tiddlers = {}
    # keep the collection ordered
    found_tiddlers_list = []
    for filter in filters:
        if 'removal' in filter[0].__dict__:
            # If the filter has been tagged as a removal filter,
            # remove the tiddlers which match the filter.
            for tiddler in filter[0](filter[1], found_tiddlers.values()):
                if tiddler.title in found_tiddlers:
                    del found_tiddlers[tiddler.title]
                    found_tiddlers_list.remove(tiddler.title)
        elif 'totaller' in filter[0].__dict__:
            # A totaller doesn't change the items in the
            # list of tiddlers. It either sorts them or
            # limits them to a certain number.

            # This turns out to be quite complicated, so we
            # do some pretty hairy manipulations on the
            # found_tiddlers and found_tiddlers_lists data.
            # I'm sure there is a better way.

            # A sorter must recreate the entire found_tiddlers_list
            # while a counter does nothing with the list.
            if len(found_tiddlers) == 0:
                for tiddler in tiddlers:
                    found_tiddlers[tiddler.title] = tiddler
                    found_tiddlers_list.append(tiddler.title)
            the_tiddlers = {}
            for tiddler in filter[0](filter[1], [found_tiddlers[title] for title in found_tiddlers_list]):
                if 'sorter' in filter[0].__dict__:
                    found_tiddlers_list.remove(tiddler.title)
                    found_tiddlers_list.append(tiddler.title)
                the_tiddlers[tiddler.title] = tiddler
            found_tiddlers = the_tiddlers
        else:
            for tiddler in filter[0](filter[1], tiddlers):
                found_tiddlers[tiddler.title] = tiddler
                if tiddler.title in found_tiddlers_list:
                    found_tiddlers_list.remove(tiddler.title)
                found_tiddlers_list.append(tiddler.title)

    return [found_tiddlers[title] for title in found_tiddlers_list \
            if title in found_tiddlers]


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


def make_field_filter(field):
    """
    Limit the number of tiddlers based on the value of a(n extended) field.
    """

    negator = 0
    remover = 0

    if field.startswith('!'):
        field = field.lstrip('!')
        negator = 1

    if field.startswith('-'):
        field = field.lstrip('-')
        remover = 1

    def field_filter(argument, tiddlers):
        return [tiddler for tiddler in tiddlers
                if field in tiddler.fields and tiddler.fields[field] == argument]

    if negator:
        return negate(field_filter)

    if remover:
        return remove(field_filter)

    return field_filter


def make_count():
    """
    Limit the number of tiddlers by the argument.
    """

    def count_filter(count, tiddlers):
        return tiddlers[0:int(count)]

    count_filter.totaller = 1
    return count_filter


def make_sort():
    """
    Sort the tiddlers we have so far
    """

    def sort_filter(field, tiddlers):
        reverse = False
        if field.find('-') == 0:
            reverse = True
            field = field[1:]
        elif field.find('+') == 0:
            field = field[1:]

        try:
            new_tiddlers = sorted(tiddlers, key=lambda x: str(getattr(x, field)).lower(), reverse=reverse)
        except AttributeError, exc:
            raise FilterError('Unable to filter: %s' % exc)
        return new_tiddlers

    sort_filter.totaller = 1
    sort_filter.sorter = 1

    return sort_filter

FILTER_MAP = {
        'tag': by_tag,
        '!tag': negate(by_tag),
        '-tag': remove(by_tag),

        'text': by_text,
        '!text': negate(by_text),
        '-text': remove(by_text),

        'bag': by_bag,
        '!bag': negate(by_bag),
        '-bag': remove(by_bag),

        'sort': make_sort(),
        'count': make_count(),

        'since': by_since,
}
