"""
HTML based serializers.
"""

import re
import urllib

from tiddlyweb.serializer import TiddlerFormatError

def list_recipes(recipes):
    """
    List the recipes on the system as html.
    """
    lines = []
    output = '<ul>\n'
    for recipe in recipes:
        line = '<li><a href="recipes/%s">%s</a></li>' % (urllib.quote(recipe.name), recipe.name)
        lines.append(line)
    output += "\n".join(lines)
    return output + '\n</ul>'

def recipe_as(recipe, sortkey):
    """
    Never sort a recipe, so ignore sortkey, but
    keep it there for sake of the interface.
    """
    lines = []
    output = '<ul>\n'
    for bag, filter in recipe:
        line = '<li><a href="'
        if type(bag) != str:
            bag = bag.name
        line += '/bags/%s/tiddlers' % urllib.quote(bag)
        if filter:
            line += '?%s' % urllib.quote(filter)
        line += '">bag: %s filter:%s</a></li>' % (bag, filter)
        lines.append(line)
    output += "\n".join(lines)
    return output + '\n</ul>'

def as_recipe(recipe, input):
    pass

def bag_as(bag, sortkey):
    """
    List the tiddlers in a bag as html.
    """
    lines = []
    output = '<ul>\n'
    for tiddler in sorted(bag.list_tiddlers(), key=sortkey):
        line = '<li><a href="tiddlers/%s">%s</a></li>' % (urllib.quote(tiddler.title), tiddler.title)
        lines.append(line)
    output += "\n".join(lines)
    return output + '\n</ul>'

def as_bag(bag, input):
    pass

def tiddler_as(tiddler, sortkey):
    pass

def as_tiddler(tiddler, input):
    pass

def as_tags(string):
    pass

def tags_as(tags, sortkey):
    pass
