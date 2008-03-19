"""
Serialize into a fullblow tiddlywiki wiki.

This is initially for the sake of testing the bits.
"""

import codecs

from text import tags_as
from tiddlyweb.bag import Bag
from tiddlyweb import filter
from tiddlyweb import control

# this should come from config or even
# from a url
empty_html = 'lib/empty.html'
splitter = '</div>\n<!--POST-STOREAREA-->\n'

def recipe_as(recipe):
    """
    Recipe as a wiki.
    """

    lines = ''
    for tiddler in control.get_tiddlers_from_recipe(recipe):
        lines += _tiddler_as_div(tiddler)

    return _put_string_in_tiddlywiki(lines)

def _put_string_in_tiddlywiki(lines):
    tiddlystart, tiddlyfinish = _split_empty_html()
    return tiddlystart + lines + splitter + tiddlyfinish

def as_recipe(recipe, input):
    pass

def _split_empty_html():
# this could throw, which is just fine, 
# that's what we want
    f = codecs.open(empty_html, encoding='utf-8')
    wiki = f.read()
    return wiki.split(splitter)

def bag_as(bag):
    lines = ''
    for tiddler in bag.list_tiddlers():
        lines += _tiddler_as_div(tiddler)

    return _put_string_in_tiddlywiki(lines)

def as_bag(bag):
    pass

def tiddler_as(tiddler):
    tiddler_div = _tiddler_as_div(tiddler)

    return _put_string_in_tiddlywiki(tiddler_div)

def _tiddler_as_div(tiddler):
    """
    Read in the tiddler from a div.
    """

    return """<div title="%s" modifier="%s" modified="%s" created="%s" tags="%s">
<pre>%s</pre>
</div>
""" % (tiddler.title, tiddler.modifier, tiddler.modified, tiddler.created, tags_as(tiddler.tags), tiddler.text)

def as_tiddler(tiddler):
    pass
