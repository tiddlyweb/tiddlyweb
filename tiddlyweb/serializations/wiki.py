"""
Serialize into a fullblown tiddlywiki wiki.
"""

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

    def bag_as(self, bag):
        lines = ''
        for tiddler in bag.list_tiddlers():
            lines += self._tiddler_as_div(tiddler)

        return self._put_string_in_tiddlywiki(lines)

    def tiddler_as(self, tiddler):
        tiddler_div = self._tiddler_as_div(tiddler)

        return self._put_string_in_tiddlywiki(tiddler_div)

    def _put_string_in_tiddlywiki(self, lines):
        tiddlystart, tiddlyfinish = self._split_empty_html()
        return tiddlystart + lines + splitter + tiddlyfinish

    def _split_empty_html(self):
# this could throw, which is just fine, 
# that's what we want
        f = open(empty_html)
        wiki = f.read()
        wiki = unicode(wiki, 'utf-8')
        return wiki.split(splitter)

    def _tiddler_as_div(self, tiddler):
        """
        Read in the tiddler from a div.
        """
        recipe_name = ''
        if tiddler.recipe:
            recipe_name = tiddler.recipe
        try: 
            host = '%s://%s:%s/' % \
                    (server_host['scheme'], server_host['host'], server_host['port'])
        except KeyError:
            host = ''

        return '<div title="%s" server.page.revision="%s" modifier="%s" server.workspace="%s" server.type="tiddlyweb" server.host="%s" server.bag="%s" modified="%s" created="%s" tags="%s">\n<pre>%s</pre>\n</div>\n' \
                % (tiddler.title, tiddler.revision, tiddler.modifier, recipe_name,
                        host, tiddler.bag, tiddler.modified, tiddler.created,
                        self.tags_as(tiddler.tags), self._html_encode(tiddler.text))

