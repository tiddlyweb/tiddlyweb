"""
Text based serializers.
"""

import re
import urllib

from tiddlyweb.serializer import TiddlerFormatError

def list_recipes(recipes):
    return "\n".join([recipe.name for recipe in recipes])

def list_bags(bags):
    return "\n".join([bag.name for bag in bags])

def recipe_as(recipe, sortkey):
    """
    Never sort a recipe, so ignore sortkey, but
    keep it there for sake of the interface.
    """
    lines = []
    for bag, filter in recipe:
        line = ''
# enable BagS in recipes
        if not isinstance(bag, basestring):
            bag = bag.name
        line += '/bags/%s/tiddlers' % urllib.quote(bag)
        if filter:
            line += '?%s' % urllib.quote(filter)
        lines.append(line)
    return "\n".join(lines)

def as_recipe(recipe, input):
    """
    Turn a string back into a recipe.
    """
    lines = input.rstrip().split('\n')
    recipe_lines = []
    for line in lines:
        if '?' in line:
            bag, filter = line.split('?')
        else:
            bag = line
            filter = ''
        bagname = urllib.unquote(bag.split('/')[2])
        filter = urllib.unquote(filter)
        recipe_lines.append([bagname, filter])
    recipe.set_recipe(recipe_lines)
    return recipe

def bag_as(bag, sortkey):
    """
    List the tiddlers in a bag as text.

    Is the bag an ordered list, so we shouldn't be sorting.
    """
    lines = []
    for tiddler in sorted(bag.list_tiddlers(), key=sortkey):
        line = 'tiddlers/%s' % urllib.quote(tiddler.title)
        lines.append(line)
    return "\n".join(lines)

def as_bag(bag, input):
    pass

def tiddler_as(tiddler, sortkey):
    return 'modifier: %s\ntags: %s\n\n%s\n' \
            % (tiddler.modifier, tags_as(tiddler.tags, sortkey), tiddler.content)

def as_tiddler(tiddler, input):
    try:
        header, content = input.split('\n\n', 1)
        tiddler.content = content
        headers = header.split('\n')

        for field, value in [x.split(': ') for x in headers]:
            setattr(tiddler, field, value)
    except ValueError, e:
        raise TiddlerFormatError, 'malformed tiddler string: %s' % e

    tag_string = tiddler.tags
    tiddler.tags = as_tags(tag_string)

    return tiddler

def as_tags(string):
    tags = []
    tag_matcher = re.compile(r'([^ \]\[]+)|(?:\[\[([^\]]+)\]\])')
    for match in tag_matcher.finditer(string):
        if match.group(2):
            tags.append(match.group(2))
        elif match.group(1):
            tags.append(match.group(1))

    return tags

def tags_as(tags, sortkey):
    tag_string_list = []
    for tag in sorted(tags, key=sortkey):
        if ' ' in tag:
            tag = '[[%s]]' % tag
        tag_string_list.append(tag)
    return ' '.join(tag_string_list)
