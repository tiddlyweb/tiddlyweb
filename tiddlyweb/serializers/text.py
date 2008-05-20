"""
Text based serializers.
"""

import urllib

from tiddlyweb.serializer import TiddlerFormatError
from tiddlyweb.serializers import SerializationInterface

class Serialization(SerializationInterface):

    def list_recipes(self, recipes):
        return "\n".join([recipe.name for recipe in recipes])

    def list_bags(self, bags):
        return "\n".join([bag.name for bag in bags])

    def recipe_as(self, recipe):
        """
        Recipe as text.
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

    def as_recipe(self, recipe, input):
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

    def bag_as(self, bag):
        """
        List the tiddlers in a bag as text.
        """
        if bag.revbag:
            return "\n".join(["%s:%s" % (tiddler.title, tiddler.revision) for tiddler in bag.list_tiddlers()])
        else:
            return "\n".join([tiddler.title for tiddler in bag.list_tiddlers()])

    def tiddler_as(self, tiddler):
        return 'modifier: %s\ncreated: %s\nmodified: %s\ntags: %s\n\n%s\n' \
                % (tiddler.modifier, tiddler.created, tiddler.modified, \
                self.tags_as(tiddler.tags), tiddler.text)

    def as_tiddler(self, tiddler, input):
        try:
            header, text = input.split('\n\n', 1)
            tiddler.text = text.rstrip()
            headers = header.split('\n')

            for field, value in [x.split(': ') for x in headers]:
                setattr(tiddler, field, value)
        except ValueError, e:
            raise TiddlerFormatError, 'malformed tiddler string: %s' % e

        tag_string = tiddler.tags
        if tag_string:
            tiddler.tags = self.as_tags(tag_string)

        return tiddler

