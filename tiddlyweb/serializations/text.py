"""
:py:class:`Serialization <tiddlyweb.serializations.SerializationInterface>`
for plain text.
"""

import simplejson

from base64 import b64encode, b64decode

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.specialbag import get_bag_retriever
from tiddlyweb.serializer import TiddlerFormatError
from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.model.policy import Policy
from tiddlyweb.util import binary_tiddler

from tiddlyweb.fixups import quote, unquote, basestring, unicode


class Serialization(SerializationInterface):
    """
    Serialize entities and collections to and from
    textual representations. This is primarily used
    by the :py:class:`text <tiddlyweb.stores.text.Store>`
    :py:class:`Store <tiddlyweb.store.Store>`.
    """

    tiddler_members = [field for field in Tiddler.data_members if not field in
            ['title', 'text', 'fields']]

    def list_recipes(self, recipes):
        """
        Return a linefeed separated list of :py:class:`recipe
        <tiddlyweb.model.recipe.Recipe>` names in the ``recipes`` list.
        """
        return ('%s\n' % recipe.name for recipe in recipes)

    def list_bags(self, bags):
        """
        Return a linefeed separated list of :py:class:`bag
        <tiddlyweb.model.bag.Bag>` names in the ``bags`` list.
        """
        return ('%s\n' % bag.name for bag in bags)

    def list_tiddlers(self, tiddlers):
        """
        Return a linefeed separated list of :py:class:`tiddler
        <tiddlyweb.model.tiddler.Tiddler>` titles in the ``tiddlers`` list.

        If the tiddlers are a collection of revisions, include the
        revision identifier.
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
        Dump a :py:class:`recipe <tiddlyweb.model.recipe.Recipe>` as text.
        """
        policy_dict = dict([(key, getattr(recipe.policy, key)) for
                key in Policy.attributes])
        lines = ['desc: %s' % recipe.desc, 'policy: %s' %
                simplejson.dumps(policy_dict), '']

        for bag, filter_string in recipe.get_recipe():
            line = ''
            if not get_bag_retriever(self.environ, bag):
                # If there is a retriever for this bag name then
                # we want to write its name straight.
                line += '/bags/%s/tiddlers' % quote(
                        bag.encode('utf-8'), safe='')
            else:
                line += bag
            if filter_string:
                line += '?%s' % filter_string
            lines.append(line)

        return "\n".join(lines)

    def as_recipe(self, recipe, input_string):
        """
        Turn a string into a :py:class:`recipe
        <tiddlyweb.model.recipe.Recipe>` if possible.
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
        Represent a :py:class:`tiddler <tiddlyweb.model.tiddler.Tiddler>`
        as a text string: headers, blank line, text.

        ``omit_*`` arguments are non-standard options, usable only when this
        method is called directly (outside the regular Serializer interface)

        If ``omit_empty`` is True, don't emit empty Tiddler members.

        ``omit_members`` can be used to provide a list of members to not
        include in the output.
        """
        omit_members = omit_members or []

        headers = []
        for member in self.tiddler_members:
            if member in omit_members:
                continue

            value = getattr(tiddler, member)
            if member == 'tags':  # XXX: special-casing
                value = self.tags_as(tiddler.tags).replace('\n', '\\n')

            if value or not omit_empty:
                if value is None:
                    value = ''
                headers.append('%s: %s' % (member, value))

        custom_fields = self.fields_as(tiddler)
        headers.extend(custom_fields)

        if binary_tiddler(tiddler):
            body = b64encode(tiddler.text).decode('UTF-8')
        else:
            body = tiddler.text

        return '%s\n\n%s\n' % ('\n'.join(headers), body)

    def fields_as(self, tiddler):
        """
        Turn extended :py:class:`tiddler <tiddlyweb.model.tiddler.Tiddler>`
        fields into RFC 822-style header strings.
        """
        fields = []
        for key in tiddler.fields:
            if hasattr(tiddler, key):
                raise TiddlerFormatError(
                        'reserved key "%s" in fields of tiddler: %s'
                        % (key, tiddler.title))
            # XXX: TiddlyWiki legacy remnant?
            if not key.startswith('server.'):
                value = unicode(tiddler.fields[key])
                fields.append('%s: %s' % (key, value.replace('\n', '\\n')))
        return fields

    def as_tiddler(self, tiddler, input_string):
        """
        Transform a text representation of a :py:class:`tiddler
        <tiddlyweb.model.tiddler.Tiddler>` into a tiddler object.
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
        except ValueError as exc:
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
                    bagname = unquote(bagname)
                else:
                    bagname = bag
                recipe_lines.append((bagname, filter_string))
        return recipe_lines
