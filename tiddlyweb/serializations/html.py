"""
HTML based serializers.
"""

import re
import urllib

from tiddlyweb.serializer import TiddlerFormatError
from tiddlyweb.serializations import SerializationInterface

class Serialization(SerializationInterface):

    def list_recipes(self, recipes):
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

    def list_bags(self, bags):
        """
        List the bags on the system as html.
        """
        lines = []
        output = '<ul>\n'
        for bag in bags:
            line = '<li><a href="bags/%s/tiddlers">%s</a></li>' % (urllib.quote(bag.name), bag.name)
            lines.append(line)
        output += "\n".join(lines)
        return output + '\n</ul>'

    def recipe_as(self, recipe):
        """
        Recipe as html.
        """
        lines = []
        output = '<ul>\n'
        for bag, filter in recipe:
            line = '<li><a href="'
            if not isinstance(bag, basestring):
                bag = bag.name
            line += '/bags/%s/tiddlers' % urllib.quote(bag)
            if filter:
                line += '?%s' % urllib.quote(filter)
            line += '">bag: %s filter:%s</a></li>' % (bag, filter)
            lines.append(line)
        output += "\n".join(lines)
        return output + '\n</ul>'

    def bag_as(self, bag):
        """
        List the tiddlers in a bag as html.
        """
        lines = []
        output = '<ul>\n'
        for tiddler in bag.list_tiddlers():
            if bag.revbag:
                line = '<li><a href="/bags/%s/tiddlers/%s/revisions/%s">%s:%s</a></li>' % (urllib.quote(tiddler.bag), urllib.quote(tiddler.title), tiddler.revision, tiddler.title, tiddler.revision)
            else:
                line = '<li><a href="/bags/%s/tiddlers/%s">%s</a></li>' % (urllib.quote(tiddler.bag), urllib.quote(tiddler.title), tiddler.title)
            lines.append(line)
        output += "\n".join(lines)
        return output + '\n</ul>'

    def tiddler_as(self, tiddler):
        return """<div title="%s" server.page.revision="%s" modifier="%s" modified="%s" created="%s" tags="%s">
    <pre>%s</pre>
    </div>
    """ % (tiddler.title, tiddler.revision, tiddler.modifier, tiddler.modified, tiddler.created, self.tags_as(tiddler.tags), tiddler.text)

