"""
Serialize into a fullblown tiddlywiki wiki.
"""

import re

from tiddlyweb.serializer import NoSerializationError
from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.web.util import server_base_url

# this should come from config or even
# from a url
empty_html = 'lib/empty.html'
splitter = '</div>\n<!--POST-STOREAREA-->\n'

class Serialization(SerializationInterface):

    def as_bag(self, bag, input_string):
        """
        Turn a wiki into a bunch of tiddlers
        stored in the bag.
        """
        try:
            from tiddlyweb.importer import import_wiki
            return import_wiki(self.environ['tiddlyweb.store'], input_string, bag.name)
        except ImportError:
            raise NoSerializationError

    def list_tiddlers(self, bag):
        return self._put_tiddlers_in_tiddlywiki(bag.list_tiddlers())

    def tiddler_as(self, tiddler):
        return self._put_tiddlers_in_tiddlywiki([tiddler], title=tiddler.title)

    def _put_tiddlers_in_tiddlywiki(self, tiddlers, title='TiddlyWeb Loading'):
# read in empty.html from somewhere (prefer url)
# replace <title> with the right stuff
## get SiteTitle tiddler
## get SiteSubTitle tiddler
## use one or both, if both ' - ' in the middel
## turn into HTML, pull plain text out of HTML
## put plain text into <title></title> of doc
# replace markup etc with the right stuff
# hork in the stuff
        lines = ''
        for tiddler in tiddlers:
            lines += self._tiddler_as_div(tiddler)
        wiki = self._get_wiki()
        wiki = self._inject_title(wiki, title)
        tiddlystart, tiddlyfinish = self._split_wiki(wiki)
        return tiddlystart + lines + splitter + tiddlyfinish

    def _inject_title(self, wiki, title):
        title = '\n<title>\n%s\n</title>\n' % title
        return re.sub('\n<title>\n[^\n]*\n</title>\n', title, wiki, count=0)

    def _get_wiki(self):
# this could throw, which is just fine, 
# that's what we want
        f = open(empty_html)
        wiki = f.read()
        wiki = unicode(wiki, 'utf-8')
        return wiki

    def _split_wiki(self, wiki):
        return wiki.split(splitter)

    def _tiddler_as_div(self, tiddler):
        """
        Read in the tiddler from a div.
        """
        recipe_name = ''
        if tiddler.recipe:
            recipe_name = tiddler.recipe
        try: 
            host = server_base_url(self.environ)
        except KeyError:
            host = ''
        host = '%s/' % host

        return '<div title="%s" server.page.revision="%s" modifier="%s" server.workspace="%s" server.type="tiddlyweb" server.host="%s" server.bag="%s" modified="%s" created="%s" tags="%s">\n<pre>%s</pre>\n</div>\n' \
                % (tiddler.title, tiddler.revision, tiddler.modifier, recipe_name,
                        host, tiddler.bag, tiddler.modified, tiddler.created,
                        self.tags_as(tiddler.tags), self._html_encode(tiddler.text))

