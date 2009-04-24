"""
Serialize into a fullblown tiddlywiki wiki.
"""

import logging
import urllib

from base64 import b64encode
            
import html5lib
from html5lib import treebuilders

from tiddlyweb.serializer import NoSerializationError
from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.web.util import server_base_url, tiddler_url, encode_name
from tiddlyweb.wikklyhtml import wikitext_to_wikklyhtml

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

    def _no_script(self, url):
        return """
<div id="javascriptWarning">
This page requires JavaScript to function properly.<br /><br />
If you do not use JavaScript you may still <a href="%s">browse
the content of this wiki</a>.
</div>
""" % url

    def _put_tiddlers_in_tiddlywiki(self, tiddlers, title='TiddlyWeb Loading'):
        """
        Take the provided tiddlers and inject them into the base_tiddlywiki,
        adjusting content for title, subtite, and the various pre and post
        head sections of the file.
        """

        if tiddlers[0].recipe:
            workspace = '/recipes/%s/tiddlers' % encode_name(tiddlers[0].recipe)
        else:
            workspace = '/bags/%s/tiddlers' % encode_name(tiddlers[0].bag)
        browsable_url = server_base_url(self.environ) + workspace

        if len(tiddlers) == 1:
            default_tiddler = Tiddler('DefaultTiddlers')
            default_tiddler.text = '[[' + tiddlers[0].title + ']]'
            tiddlers = [tiddlers[0], default_tiddler]

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

        wiki = self._replace_chunk(wiki, '\n<noscript>\n', '\n</noscript>\n', self._no_script(browsable_url))

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
        """
        Take a string that may be HTML and turn it
        into plain text by finding all the included
        text.
        """
        output = wikitext_to_wikklyhtml('', '', unicode(title))
        parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('beautifulsoup'))
        soup = parser.parse(output)
        title = soup.findAll(text=True)
        return ''.join(title).rstrip().lstrip()

    def _determine_title(self, title, candidate_title, candidate_subtitle):
        """
        Create a title for the wiki file from various
        optional inputs.
        """
        if candidate_title and candidate_subtitle:
            return '%s - %s' % (candidate_title, candidate_subtitle)
        if candidate_title:
            return candidate_title
        if candidate_subtitle:
            return candidate_subtitle
        return title

    def _inject_title(self, wiki, title):
        """
        Replace the title in the base_tiddlywiki
        with our title.
        """
        return self._replace_chunk(wiki, '\n<title>\n', '\n</title>\n', title)

    def _replace_chunk(self, wiki, start, finish, replace):
        """
        Find the index of start and finish in the string, and
        replace the part in between with replace.
        """
        try:
            sindex = wiki.index(start)
            findex = wiki.index(finish) + len(finish)
            return wiki[0:sindex] + start + replace + finish + wiki[findex:]
        except ValueError:
            return wiki

    def _get_wiki(self):
        """
        Read base_tiddlywiki from its location.
        """
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

        return ('<div title="%s" server.title="%s" server.page.revision="%s" '
                'modifier="%s" server.workspace="bags/%s" '
                'server.type="tiddlyweb" server.host="%s" '
                'server.recipe="%s" server.bag="%s" server.permissions="%s" '
                'modified="%s" created="%s" tags="%s" %s>\n'
                '<pre>%s</pre>\n</div>\n'
                % (tiddler.title, tiddler.title, tiddler.revision,
                        tiddler.modifier, tiddler.bag, host, recipe_name,
                        tiddler.bag, self._tiddler_permissions(tiddler),
                        tiddler.modified, tiddler.created,
                        self.tags_as(tiddler.tags),
                        self._tiddler_fields(tiddler.fields),
                        self._html_encode(tiddler_output)))

    def _tiddler_permissions(self, tiddler):
        """
        Make a list of the permissions the current user has
        on this tiddler.
        """

        def _read_bag_perms(environ, tiddler):
            perms = []
            if 'tiddlyweb.usersign' in environ:
                store = tiddler.store
                if store:
                    bag = Bag(tiddler.bag)
                    bag = store.get(bag)
                    perms = bag.policy.user_perms(environ['tiddlyweb.usersign'])
            return perms

        perms = []
        bag_name = tiddler.bag
        if hasattr(self, 'bag_perms_cache'):
            if bag_name in self.bag_perms_cache:
                perms = self.bag_perms_cache[bag_name]
            else:
                perms = _read_bag_perms(self.environ, tiddler)
        else:
            self.bag_perms_cache = {}
            perms = _read_bag_perms(self.environ, tiddler)
        self.bag_perms_cache[bag_name] = perms
        return ', '.join(perms)

    def _binary_tiddler(self, tiddler):
        """
        Make the content for a tiddler that has non-wikitext content.

        Base64 encode if the stuff is small enough for browsers to handle.
        """
        b64text = b64encode(tiddler.text)
        if b64text < 32 * 1024:
            return 'data:$s;base64,%s' % (tiddler.type, b64text)
        else:
            if tiddler.type.startswith('image'):
                return '\n<html><img src="%s" /></html>\n' % tiddler_url(self.environ, tiddler)
            else:
                return '\n<html><a href="%s">%s</a></html>\n' % (tiddler_url(self.environ, tiddler), tiddler.title)

    def _tiddler_fields(self, fields):
        """
        Turn tiddler fields into a string suitable for
        a div attribute.
        """
        output = []
        for key in fields:
            output.append('%s="%s"' % (key, fields[key]))
        return ' '.join(output)
