"""
Text based serializers.
"""

import urllib

def recipe_as(recipe):
    lines = []
    for bag, filter in recipe:
        line = ''
# enable BagS in recipes
        if type(bag) != '':
            bag = bag.name
        line += '/bags/%s' % urllib.quote(bag)
        if filter:
            line += '?%s' % urllib.quote(filter)
        lines.append(line)
    return "\n".join(lines)

def tiddler_as(tiddler):
    return 'name: %s\nauthor: %s\ntags: %s\n\n%s\n' \
            % (tiddler.name, tiddler.author, tags_as(tiddler.tags), tiddler.content)

def tags_as(tags):
    tag_string_list = []
    for tag in tags:
        if ' ' in tag:
            tag = '[[%s]]' % tag
        tag_string_list.append(tag)
    return ' '.join(tag_string_list)
