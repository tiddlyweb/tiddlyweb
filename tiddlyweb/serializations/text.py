"""
Text based serializers.
"""

import urllib
import simplejson

from base64 import b64encode, b64decode

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.specialbag import get_bag_retriever
from tiddlyweb.serializer import TiddlerFormatError
from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.model.policy import Policy
from tiddlyweb.util import binary_tiddler


class Serialization(SerializationInterface):
    """
    Serialize entities and collections to and from
    textual representations. This is primarily used
    by the text Store.
    """

    tiddler_members = [field for field in Tiddler.data_members if not field in
            ['title', 'text', 'fields']]

    def list_recipes(self, recipes):
        """
        Return a linefeed separated list of recipe names.
        """
        return ('%s\n' % recipe.name for recipe in recipes)

    def list_bags(self, bags):
        """
        Return a linefeed separated list of recipe names.
        """
        return ('%s\n' % bag.name for bag in bags)

    def list_tiddlers(self, tiddlers):
        """
        List the tiddlers as text.
        """
        tiddlers.store = None
        if hasattr(tiddlers, 'is_revisions') and tiddlers.is_revisions:
            for tiddler in tiddlers:
                yield "%s:%s\n" % (tiddler.title, tiddler.revision)
        else:
            for tiddler in tiddlers:
                yield "%s\n" % tiddler.title
        return

    def recipe_as(self, recipe):
        """
        Recipe as text.
        """
        policy_dict = dict([(key, getattr(recipe.policy, key)) for
                key in Policy.attributes])
        lines = ['desc: %s' % recipe.desc, 'policy: %s' %
                simplejson.dumps(policy_dict), '']

        for bag, filter_string in recipe.get_recipe():
            line = ''
            if not isinstance(bag, basestring):
                bag = bag.name
            if not get_bag_retriever(self.environ, bag):
                # If there is a retriever for this bag name then
                # we want to write its name straight.
                line += '/bags/%s/tiddlers' % urllib.quote(
                        bag.encode('utf-8'), safe='')
            else:
                line += bag
            if filter_string:
                line += '?%s' % filter_string
            lines.append(line)

        return "\n".join(lines)

    def as_recipe(self, recipe, input_string):
        """
        Turn a string back into a recipe.
        """

        def _handle_headers(recipe, header):
            """
            Parse recipe headers from text.
            """
            headers = header.split('\n')
            for field, value in [x.split(': ', 1) for x in headers]:
                if field == 'policy':
                    recipe.policy = Policy()
                    info = simplejson.loads(value)
                    for key, value in info.items():
                        recipe.policy.__setattr__(key, value)
                else:
                    setattr(recipe, field, value)

        try:
            header, body = input_string.rstrip().split('\n\n', 1)
            _handle_headers(recipe, header)
        except ValueError:
            body = input_string.rstrip()
            if body.startswith('desc:'):
                header = body
                body = ''
                _handle_headers(recipe, header)

        recipe_lines = self._recipe_lines(body)
        recipe.set_recipe(recipe_lines)
        return recipe

    def tiddler_as(self, tiddler, omit_empty=False, omit_members=None):
        """
        Represent a tiddler as a text string: headers, blank line, text.

        `omit_*` arguments are non-standard options, usable only when this
        method is called directly (outside the regular Serializer interface)

        If `omit_empty` is True, don't emit empty Tiddler members.

        `omit_members` can represent a list of members to not include
        in the output.
        """
        omit_members = omit_members or []

        headers = []
        for member in self.tiddler_members:
            if member in omit_members:
                continue

            value = getattr(tiddler, member)
            if member == 'tags': # XXX: special-casing
                value = self.tags_as(tiddler.tags).replace('\n', '\\n')

            if value or not omit_empty:
                if value is None:
                    value = ''
                headers.append('%s: %s' % (member, value))

        custom_fields = self.fields_as(tiddler)
        headers.extend(custom_fields)

        if binary_tiddler(tiddler):
            body = b64encode(tiddler.text)
        else:
            body = tiddler.text

        return '%s\n\n%s\n' % ('\n'.join(headers), body)

    def fields_as(self, tiddler):
        """
        Turn extended tiddler fields into RFC 822-style header strings.
        """
        fields = []
        for key in tiddler.fields:
            if not key.startswith('server.'): # XXX: TiddlyWiki legacy remnant?
                value = unicode(tiddler.fields[key])
                fields.append('%s: %s' % (key, value.replace('\n', '\\n')))
        return fields

    def as_tiddler(self, tiddler, input_string):
        """
        Transform a text representation of a tiddler into
        tiddler attributes.
        """
        try:
            header, text = input_string.split('\n\n', 1)
            tiddler.text = text.rstrip()
            headers = header.split('\n')

            for field, value in [x.split(': ', 1) for x in headers]:
                if value == '':
                    continue
                if hasattr(tiddler, field):
                    setattr(tiddler, field, value)
                else:
                    tiddler.fields[field] = value.replace('\\n', '\n')
        except ValueError, exc:
            raise TiddlerFormatError('bad headers in tiddler: %s, %s' %
                    (tiddler.title, exc))

        # In some strange situations tiddler.tags will not
        # be a string here, so will still have its default
        # value of [], which we want to keep.
        if isinstance(tiddler.tags, basestring):
            tag_string = tiddler.tags
            if tag_string:
                tiddler.tags = self.as_tags(tag_string)

        # If this is a binary tiddler, clean up.
        if binary_tiddler(tiddler):
            tiddler.text = b64decode(tiddler.text.lstrip().rstrip())

        return tiddler

    def _recipe_lines(self, body):
        """
        Given text containing a list of recipes, calculate
        the recipe information they hold and return
        as a list of bagname, filter lists.
        """
        recipe_lines = []
        if len(body):
            lines = body.rstrip().split('\n')
            for line in lines:
                if '?' in line:
                    bag, query_string = line.split('?')
                    filter_string = query_string
                else:
                    bag = line
                    filter_string = ''
                if bag.startswith('/bags/'):
                    bagname = bag.split('/')[2]
                    bagname = urllib.unquote(bagname.encode('utf-8'))
                    bagname = bagname.decode('utf-8')
                else:
                    bagname = bag
                recipe_lines.append((bagname, filter_string))
        return recipe_lines
