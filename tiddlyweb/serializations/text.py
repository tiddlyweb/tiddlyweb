"""
Text based serializers.
"""

import urllib
import cgi

from tiddlyweb.serializations import SerializationInterface

class Serialization(SerializationInterface):
    """
    Serialize entities and collections to and from
    textual representations. This is primarily used
    by the text Store.
    """

    def list_recipes(self, recipes):
        """
        Return a linefeed separated list of recipe names.
        """
        return "\n".join([recipe.name for recipe in recipes])

    def list_bags(self, bags):
        """
        Return a linefeed separated list of recipe names.
        """
        return "\n".join([bag.name for bag in bags])

    def recipe_as(self, recipe):
        """
        Recipe as text.
        """
        lines = ['desc: %s' % recipe.desc, '']
        for bag, filter in recipe:
            line = ''
# enable BagS in recipes
            if not isinstance(bag, basestring):
                bag = bag.name
            line += '/bags/%s/tiddlers' % bag
            if filter:
                line += '?filter=%s' % filter
            lines.append(line)
        return "\n".join(lines)

    def as_recipe(self, recipe, input):
        """
        Turn a string back into a recipe.
        """
        try:
            header, body = input.rstrip().split('\n\n', 1)
            headers = header.split('\n')
            for field, value in [x.split(': ') for x in headers]:
                setattr(recipe, field, value)
        except ValueError:
            body = input.rstrip()

        recipe_lines = self._recipe_lines(body)
        recipe.set_recipe(recipe_lines)
        return recipe

    def list_tiddlers(self, bag):
        """
        List the tiddlers in a bag as text.
        """
        if bag.revbag:
            return "\n".join([
                "%s:%s" % (tiddler.title, tiddler.revision)
                for tiddler in bag.list_tiddlers()
                ])
        else:
            return "\n".join([
                tiddler.title for tiddler in bag.list_tiddlers()])

    def tiddler_as(self, tiddler):
        """
        Represent a tiddler as a text string: headers, blank line, text.
        """
        return 'modifier: %s\ncreated: %s\nmodified: %s\ntags: %s%s\n%s\n' \
                % (tiddler.modifier, tiddler.created, tiddler.modified, \
                self.tags_as(tiddler.tags), self.fields_as(tiddler), tiddler.text)

    def fields_as(self, tiddler):
        info = '\n'
        for key in tiddler.fields:
            if not key.startswith('server.'):
                info += '%s: %s\n' % (key, tiddler.fields[key])
        return info

    def as_tiddler(self, tiddler, input):
        """
        Transform a text representation of a tiddler into
        tiddler attributes.
        """
        header, text = input.split('\n\n', 1)
        tiddler.text = text.rstrip()
        headers = header.split('\n')

        for field, value in [x.split(': ') for x in headers]:
            try:
                setattr(tiddler, field, value)
            except AttributeError:
                tiddler.fields[field] = value

        # we used to raise TiddlerFormatError but there are
        # currently no rules for that...

        tag_string = tiddler.tags
        if tag_string:
            tiddler.tags = self.as_tags(tag_string)

        return tiddler

    def _recipe_lines(self, body):
        """
        Given text containing a list of recipes, calculate
        the recipe information they hold and return
        as a list of bagname, filter lists.
        """
        lines = body.rstrip().split('\n')
        recipe_lines = []
        for line in lines:
            if '?' in line:
                bag, query_string = line.split('?')
                request_info = cgi.parse_qs(query_string)
                filter = request_info.get('filter', [''])[0]
            else:
                bag = line
                filter = ''
            bagname = urllib.unquote(bag.split('/')[2])
            recipe_lines.append([bagname, filter])
        return recipe_lines
