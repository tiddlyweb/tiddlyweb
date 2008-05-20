"""
Serialize into a fullblow tiddlywiki wiki.

This is initially for the sake of testing the bits.
"""

import codecs

from tiddlyweb.bag import Bag
from tiddlyweb import filter
from tiddlyweb import control
from tiddlyweb.web.serve import server_host
from tiddlyweb.serializations import SerializationInterface

# this should come from config or even
# from a url
empty_html = 'lib/empty.html'
splitter = '</div>\n<!--POST-STOREAREA-->\n'

class Serialization(SerializationInterface):

    def recipe_as(self, recipe):
        """
        Recipe as a wiki.
        """

        lines = ''
        for tiddler in control.get_tiddlers_from_recipe(recipe):
            lines += self._tiddler_as_div(tiddler, recipe.name)

        return self._put_string_in_tiddlywiki(lines)

    def bag_as(self, bag):
        lines = ''
        for tiddler in bag.list_tiddlers():
            lines += self._tiddler_as_div(tiddler)

        return self._put_string_in_tiddlywiki(lines)

    def tiddler_as(self, tiddler):
        tiddler_div = self._tiddler_as_div(tiddler)

        return self._put_string_in_tiddlywiki(tiddler_div)

    def tags_as(self, tags):
        tag_string_list = []
        for tag in tags:
            if ' ' in tag:
                tag = '[[%s]]' % tag
            tag_string_list.append(tag)
        return ' '.join(tag_string_list)

    def _put_string_in_tiddlywiki(self, lines):
        tiddlystart, tiddlyfinish = self._split_empty_html()
        return tiddlystart + lines + splitter + tiddlyfinish

    def _split_empty_html(self):
# this could throw, which is just fine, 
# that's what we want
        f = codecs.open(empty_html, encoding='utf-8')
        wiki = f.read()
        return wiki.split(splitter)

    def _tiddler_as_div(self, tiddler, recipe_name=''):
        """
        Read in the tiddler from a div.
        """
        try: 
            host = '%s://%s:%s/' % \
                    (server_host['scheme'], server_host['host'], server_host['port'])
        except KeyError:
            host = ''

        return '<div title="%s" server.page.revision="%s" modifier="%s" server.workspace="%s" server.type="tiddlyweb" server.host="%s" server.bag="%s" modified="%s" created="%s" tags="%s">\n<pre>%s</pre>\n</div>' \
                % (tiddler.title, tiddler.revision, tiddler.modifier, recipe_name,
                        host, tiddler.bag, tiddler.modified, tiddler.created,
                        self.tags_as(tiddler.tags), tiddler.text)

