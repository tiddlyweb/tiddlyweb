"""
Selection routines.
"""

from tiddlyweb.filters.sort import ATTRIBUTE_ALTER

def tag_in_tags(tiddler, attribute, value):
    return value in tiddler.tags

def text_in_text(tiddler, attribute, value):
    return value in tiddler.text


ATTRIBUTE_SELECTOR = {
        'tag': tag_in_tags,
        'text': text_in_text,
        }


def default_func(tiddler, attribute, value):
    try:
        return getattr(tiddler, attribute) == value
    except AttributeError:
        try:
            return tiddler.fields[attribute] == value
        except KeyError:
            return False


def select_by_attribute(attribute, value, tiddlers, negate=False):
    select = ATTRIBUTE_SELECTOR.get(attribute, default_func)
    if negate:
        return [tiddler for tiddler in tiddlers if not select(tiddler, attribute, value)]
    else:
        return [tiddler for tiddler in tiddlers if select(tiddler, attribute, value)]


def select_relative_attribute(attribute, value, tiddlers, greater=False, lesser=False):

    func = ATTRIBUTE_ALTER.get(attribute, lambda x : x.lower())

    if greater:
        return [tiddler for tiddler in tiddlers if func(getattr(tiddler, attribute)) > func(value)]
    elif lesser:
        return [tiddler for tiddler in tiddlers if func(getattr(tiddler, attribute)) < func(value)]
    else:
        return tiddlers
