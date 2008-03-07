"""
Serialize into a fullblow tiddlywiki wiki.

This is initially for the sake of testing the bits.
"""

from text import tags_as
from tiddlyweb.bag import Bag
from tiddlyweb import filter

# this should come from config or even
# from a url
empty_html = 'lib/empty.html'
splitter = '</div>\n<!--POST-STOREAREA-->\n'

def recipe_as(recipe, sortkey):
    """
    Never sort a recipe, so ignore sortkey, but
    keep it there for sake of the interface.
    """
    tiddlystart, tiddlyfinish = _split_empty_html()

    lines = ''
    for tiddler in recipe.get_tiddlers():
        lines += tiddler_as(tiddler, sortkey=None)

    return tiddlystart + lines + splitter + tiddlyfinish

def as_recipe(recipe, input):
    pass

def _split_empty_html():
# this could throw, which is just fine, 
# that's what we want
    f = open(empty_html)
    wiki = f.read()
    return wiki.split(splitter)

def bag_as(bag, sortkey):
    return ''

def tiddler_as(tiddler, sortkey):
    """
    sortkey is not used, but we've got the interface to concern
    ourselves with. This seems awkward.
    """

    return """<div title="%s" modifier="%s" tags="%s">
<pre>%s</pre>
</div>
""" % (tiddler.title, tiddler.modifier, tags_as(tiddler.tags, None), tiddler.content)
