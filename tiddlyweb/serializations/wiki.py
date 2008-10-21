"""
Serialize into a fullblown tiddlywiki wiki.
"""

from base64 import b64encode

from tiddlyweb.serializer import NoSerializationError
from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.web.util import server_base_url, tiddler_url

SPLITTER = '</div>\n<!--POST-STOREAREA-->\n'

MARKUPS = {
        'MarkupPreHead': 'PRE-HEAD',
        'MarkupPostHead': 'POST-HEAD',
        'MarkupPreBody': 'PRE-BODY',
        'MarkupPostBody': 'POST-SCRIPT',
        }


class Serialization(SerializationInterface):
    """
    Serialize entities and collections to and from
    TiddlyWiki representations. This is primarily
    used to create TiddlyWikis from bags, recipes
    and tiddlers. It can also be used to import
    TiddlyWikis into the system.
    """

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
        """
        Take the tiddlers from the given bag and inject
        them into a TiddlyWiki.
        """
        return self._put_tiddlers_in_tiddlywiki(bag.list_tiddlers())

    def tiddler_as(self, tiddler):
        """
        Take the single tiddler provided and inject it into
        a TiddlyWiki.
        """
        return self._put_tiddlers_in_tiddlywiki([tiddler], title=tiddler.title)

    def _put_tiddlers_in_tiddlywiki(self, tiddlers, title='TiddlyWeb Loading'):
# read in empty.html from somewhere (prefer url)
# replace <title> with the right stuff
# replace markup etc with the right stuff
# hork in the stuff

        # figure out the content to be pushed into the
        # wiki and calculate the title
        lines = ''
        candidate_title = None
        candidate_subtitle = None
        markup_tiddlers = MARKUPS.keys()
        found_markup_tiddlers = {}
        for tiddler in tiddlers:
            lines += self._tiddler_as_div(tiddler)
            if tiddler.title == 'SiteTitle':
                candidate_title = tiddler.text
            if tiddler.title == 'SiteSubtitle':
                candidate_subtitle = tiddler.text
            if tiddler.title in markup_tiddlers:
                found_markup_tiddlers[tiddler.title] = tiddler.text

        # Turn the title into HTML and then turn it into
        # plain text so it is of a form satisfactory to <title>
        title = self._determine_title(title, candidate_title, candidate_subtitle)
        title = self._plain_textify_string(title)

        # load the wiki
        wiki = self._get_wiki()
        # put the title in place
        wiki = self._inject_title(wiki, title)

        # replace the markup bits
        if len(found_markup_tiddlers):
            for title in found_markup_tiddlers:
                start = '\n<!--%s-START-->\n' % MARKUPS[title]
                finish = '\n<!--%s-END-->\n' % MARKUPS[title]
                wiki = self._replace_chunk(wiki, start, finish, found_markup_tiddlers[title])

        # split the wiki into the before store and after store
        # sections, put our content in the middle
        tiddlystart, tiddlyfinish = wiki.split(SPLITTER, 2)
        return tiddlystart + lines + SPLITTER + tiddlyfinish

    def _plain_textify_string(self, title):
        try:
            # If the HTML serialization doesn't have wikklytext
            # we will get back wikitext inside the div classed
            # 'tiddler' instead of HTML
            from tiddlyweb.wikklyhtml import wikitext_to_wikklyhtml
            output = wikitext_to_wikklyhtml('', '', unicode(title))

            from BeautifulSoup import BeautifulSoup
            soup = BeautifulSoup(output)
            title = soup.findAll(text=True)
            return ''.join(title).rstrip().lstrip()
        except ImportError:
            # If we have been unable to load BeautifilSoup then
            # fall back to the original wikitext
            return title

    def _determine_title(self, title, candidate_title, candidate_subtitle):
        if candidate_title and candidate_subtitle:
            return '%s - %s' % (candidate_title, candidate_subtitle)
        if candidate_title:
            return candidate_title
        if candidate_subtitle:
            return candidate_subtitle
        return title

    def _inject_title(self, wiki, title):
        return self._replace_chunk(wiki, '\n<title>\n', '\n</title>\n', title)

    def _replace_chunk(self, wiki, start, finish, replace):
        try:
            sindex = wiki.index(start)
            findex = wiki.index(finish) + len(finish)
            return wiki[0:sindex] + start + replace + finish + wiki[findex:]
        except ValueError:
            return wiki

    def _get_wiki(self):
        base_tiddlywiki = open(self.environ['tiddlyweb.config']['base_tiddlywiki'])
        wiki = base_tiddlywiki.read()
        base_tiddlywiki.close()
        wiki = unicode(wiki, 'utf-8')
        return wiki

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

        if tiddler.type and tiddler.type != 'None':
            tiddler_output = self._binary_tiddler(tiddler)
        else:
            tiddler_output = tiddler.text

        return '<div title="%s" server.page.revision="%s" modifier="%s" server.workspace="%s" server.type="tiddlyweb" server.host="%s" server.bag="%s" modified="%s" created="%s" tags="%s" %s>\n<pre>%s</pre>\n</div>\n' \
                % (tiddler.title, tiddler.revision, tiddler.modifier, recipe_name,
                        host, tiddler.bag, tiddler.modified, tiddler.created,
                        self.tags_as(tiddler.tags), self._tiddler_fields(tiddler.fields),
                        self._html_encode(tiddler_output))

    def _binary_tiddler(self, tiddler):
        b64text = b64encode(tiddler.text)
        if b64text < 32 * 1024:
            if tiddler.type.startswith('image'):
                return '\n<html><img src="data:%s;base64,%s" /></html>\n' % \
                        (tiddler.type, b64text)
            else:
                return '\n<html><a href="data:%s;base64,%s">%s</a></html>\n' % \
                        (tiddler.type, b64text, tiddler.title)
        else:
            if tiddler.type.startswith('image'):
                return '\n<html><img src="%s" /></html>\n' % tiddler_url(self.environ, tiddler)
            else:
                return '\n<html><a href="%s">%s</a></html>\n' % (tiddler_url(self.environ, tiddler), tiddler.title)

    def _tiddler_fields(self, fields):
        output = []
        for key in fields:
            output.append('%s="%s"' % (key, fields[key]))
        return ' '.join(output)
