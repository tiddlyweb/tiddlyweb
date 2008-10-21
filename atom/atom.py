"""
Atom feeds for tiddlyweb.

The Atom code is borrowed from Django's django/utils/feedgenerator.py

  http://www.djangoproject.com/documentation/syndication_feeds/
  http://code.djangoproject.com/browser/django/trunk/django/utils/feedgenerator.py

Which appears to be licensed with

PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2

Thanks to those guys for making a feed library that hides the 
nasty XML details.

"""

import time
import types
import urllib
import datetime
import re
import email.Utils

from xml.sax.saxutils import XMLGenerator


from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.serializations.html import Serialization as HTMLSerialization
from tiddlyweb.wikklyhtml import wikitext_to_wikklyhtml

class Serialization(HTMLSerialization):

    def __init__(self, environ={}):
        self.environ = environ

    def list_recipes(self, recipes):
        pass

    def list_bags(self, bags):
        pass

    def recipe_as(self, recipe):
        pass

    def list_tiddlers(self, bag):
        """
        Turn the contents of a bag into an Atom Feed.
        """
        tiddlers = bag.list_tiddlers()
        recipe = tiddlers[0].recipe

        if recipe:
            feed = Atom1Feed(
                    title=u'Tiddlers in Recipe %s' % recipe,
                    link=u'%srecipes/%s/tiddlers' % (self._server_url(), iri_to_uri(recipe)),
                    language=u'en',
                    description=u'the tiddlers of recipe %s' % recipe
                    )
        else:
            feed = Atom1Feed(
                    title=u'Tiddlers in Bag %s' % bag.name,
                    link=u'%sbags/%s/tiddlers' % (self._server_url(), iri_to_uri(bag.name)),
                    language=u'en',
                    description=u'the tiddlers of bag %s' % bag.name
                    )
        for tiddler in tiddlers:
            self._add_tiddler_to_feed(feed, tiddler)

        # can we avoid sending utf-8 and let the wrapper handle it?
        return feed.writeString('utf-8')

    def tiddler_as(self, tiddler):
        if tiddler.recipe:
            link = u'%srecipes/%s/tiddlers/%s' % \
                    (self._server_url(), iri_to_uri(tiddler.recipe), iri_to_uri(tiddler.title))
        else:
            link = u'%sbags/%s/tiddlers/%s' % \
                    (self._server_url(), iri_to_uri(tiddler.bag), iri_to_uri(tiddler.title))
        feed = Atom1Feed(
                title=u'%s' % tiddler.title,
                link=link,
                language=u'en',
                description=u'tiddler %s' % tiddler.title
                )
        self._add_tiddler_to_feed(feed, tiddler)
        return feed.writeString('utf-8')

    def _add_tiddler_to_feed(self, feed, tiddler):
        if tiddler.recipe:
            tiddler_link = 'recipes/%s/tiddlers' % tiddler.recipe
            link = u'%srecipes/%s/tiddlers/%s' % \
                    (self._server_url(), iri_to_uri(tiddler.recipe), iri_to_uri(tiddler.title))
        else:
            tiddler_link = 'bags/%s/tiddlers' % tiddler.bag
            link = u'%sbags/%s/tiddlers/%s' % \
                    (self._server_url(), iri_to_uri(tiddler.bag), iri_to_uri(tiddler.title))

        if tiddler.type and tiddler.type != 'None':
            description = 'Binary Content'
        else:
            description = wikitext_to_wikklyhtml(self._server_url(), tiddler_link, tiddler.text)
        feed.add_item(title=tiddler.title,
                link=link,
                description=description,
                author_name=tiddler.modifier,
                pubdate=self._tiddler_datetime(tiddler.modified)
                )

    def _tiddler_datetime(self, date_string):
        return datetime.datetime(*(time.strptime(date_string, '%Y%m%d%H%M')[0:6]))

    def _server_url(self):
        try:
            server_host = self.environ['tiddlyweb.config']['server_host']
            port = str(server_host['port'])
            if port == '80' or port == '443':
                port = ''
            else:
                port = ':%s' % port
            host = '%s://%s%s/' % (server_host['scheme'], server_host['host'], port)
        except KeyError:
            host = '/'
        return host

"""
Atom feed generation from django.
"""

class SimplerXMLGenerator(XMLGenerator):
    def addQuickElement(self, name, contents=None, attrs=None):
        "Convenience method for adding an element with no children"
        if attrs is None: attrs = {}
        self.startElement(name, attrs)
        if contents is not None:
            self.characters(contents)
        self.endElement(name)

def force_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_unicode, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int, long, datetime.datetime, datetime.date, datetime.time, float)):
        return s
    if not isinstance(s, basestring,):
        if hasattr(s, '__unicode__'):
            s = unicode(s)
        else:
            s = unicode(str(s), encoding, errors)
    elif not isinstance(s, unicode):
        # Note: We use .decode() here, instead of unicode(s, encoding,
        # errors), so that if s is a SafeString, it ends up being a
        # SafeUnicode at the end.
        s = s.decode(encoding, errors)
    return s

def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    elif not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s

def iri_to_uri(iri):
    """
    Convert an Internationalized Resource Identifier (IRI) portion to a URI
    portion that is suitable for inclusion in a URL.

    This is the algorithm from section 3.1 of RFC 3987.  However, since we are
    assuming input is either UTF-8 or unicode already, we can simplify things a
    little from the full method.

    Returns an ASCII string containing the encoded result.
    """
    # The list of safe characters here is constructed from the printable ASCII
    # characters that are not explicitly excluded by the list at the end of
    # section 3.1 of RFC 3987.
    if iri is None:
        return iri
    return urllib.quote(smart_str(iri), safe='/#%[]=:;$&()+,!?*')


"""
Syndication feed generation library -- used for generating RSS, etc.

Sample usage:

>>> from django.utils import feedgenerator
>>> feed = feedgenerator.Rss201rev2Feed(
...     title=u"Poynter E-Media Tidbits",
...     link=u"http://www.poynter.org/column.asp?id=31",
...     description=u"A group weblog by the sharpest minds in online media/journalism/publishing.",
...     language=u"en",
... )
>>> feed.add_item(title="Hello", link=u"http://www.holovaty.com/test/", description="Testing.")
>>> fp = open('test.rss', 'w')
>>> feed.write(fp, 'utf-8')
>>> fp.close()
"""

def rfc2822_date(date):
    return email.Utils.formatdate(time.mktime(date.timetuple()))

def rfc3339_date(date):
    if date.tzinfo:
        return date.strftime('%Y-%m-%dT%H:%M:%S%z')
    else:
        return date.strftime('%Y-%m-%dT%H:%M:%SZ')

def get_tag_uri(url, date):
    "Creates a TagURI. See http://diveintomark.org/archives/2004/05/28/howto-atom-id"
    tag = re.sub('^http://', '', url)
    if date is not None:
        tag = re.sub('/', ',%s:/' % date.strftime('%Y-%m-%d'), tag, 1)
    tag = re.sub('#', '/', tag)
    return u'tag:' + tag

class SyndicationFeed(object):
    "Base class for all syndication feeds. Subclasses should provide write()"
    def __init__(self, title, link, description, language=None, author_email=None,
            author_name=None, author_link=None, subtitle=None, categories=None,
            feed_url=None, feed_copyright=None, feed_guid=None, ttl=None):
        to_unicode = lambda s: force_unicode(s, strings_only=True)
        if categories:
            categories = [force_unicode(c) for c in categories]
        self.feed = {
            'title': to_unicode(title),
            'link': iri_to_uri(link),
            'description': to_unicode(description),
            'language': to_unicode(language),
            'author_email': to_unicode(author_email),
            'author_name': to_unicode(author_name),
            'author_link': iri_to_uri(author_link),
            'subtitle': to_unicode(subtitle),
            'categories': categories or (),
            'feed_url': iri_to_uri(feed_url),
            'feed_copyright': to_unicode(feed_copyright),
            'id': feed_guid or link,
            'ttl': ttl,
        }
        self.items = []

    def add_item(self, title, link, description, author_email=None,
        author_name=None, author_link=None, pubdate=None, comments=None,
        unique_id=None, enclosure=None, categories=(), item_copyright=None, ttl=None):
        """
        Adds an item to the feed. All args are expected to be Python Unicode
        objects except pubdate, which is a datetime.datetime object, and
        enclosure, which is an instance of the Enclosure class.
        """
        to_unicode = lambda s: force_unicode(s, strings_only=True)
        if categories:
            categories = [to_unicode(c) for c in categories]
        self.items.append({
            'title': to_unicode(title),
            'link': iri_to_uri(link),
            'description': to_unicode(description),
            'author_email': to_unicode(author_email),
            'author_name': to_unicode(author_name),
            'author_link': iri_to_uri(author_link),
            'pubdate': pubdate,
            'comments': to_unicode(comments),
            'unique_id': to_unicode(unique_id),
            'enclosure': enclosure,
            'categories': categories or (),
            'item_copyright': to_unicode(item_copyright),
            'ttl': ttl,
        })

    def num_items(self):
        return len(self.items)

    def write(self, outfile, encoding):
        """
        Outputs the feed in the given encoding to outfile, which is a file-like
        object. Subclasses should override this.
        """
        raise NotImplementedError

    def writeString(self, encoding):
        """
        Returns the feed in the given encoding as a string.
        """
        from StringIO import StringIO
        s = StringIO()
        self.write(s, encoding)
        return s.getvalue()

    def latest_post_date(self):
        """
        Returns the latest item's pubdate. If none of them have a pubdate,
        this returns the current date/time.
        """
        updates = [i['pubdate'] for i in self.items if i['pubdate'] is not None]
        if len(updates) > 0:
            updates.sort()
            return updates[-1]
        else:
            return datetime.datetime.now()

class Enclosure(object):
    "Represents an RSS enclosure"
    def __init__(self, url, length, mime_type):
        "All args are expected to be Python Unicode objects"
        self.length, self.mime_type = length, mime_type
        self.url = iri_to_uri(url)

class Atom1Feed(SyndicationFeed):
    # Spec: http://atompub.org/2005/07/11/draft-ietf-atompub-format-10.html
    mime_type = 'application/atom+xml'
    ns = u"http://www.w3.org/2005/Atom"
    def write(self, outfile, encoding):
        handler = SimplerXMLGenerator(outfile, encoding)
        handler.startDocument()
        if self.feed['language'] is not None:
            handler.startElement(u"feed", {u"xmlns": self.ns, u"xml:lang": self.feed['language']})
        else:
            handler.startElement(u"feed", {u"xmlns": self.ns})
        handler.addQuickElement(u"title", self.feed['title'])
        handler.addQuickElement(u"link", "", {u"rel": u"alternate", u"href": self.feed['link']})
        if self.feed['feed_url'] is not None:
            handler.addQuickElement(u"link", "", {u"rel": u"self", u"href": self.feed['feed_url']})
        handler.addQuickElement(u"id", self.feed['id'])
        handler.addQuickElement(u"updated", rfc3339_date(self.latest_post_date()).decode('ascii'))
        if self.feed['author_name'] is not None:
            handler.startElement(u"author", {})
            handler.addQuickElement(u"name", self.feed['author_name'])
            if self.feed['author_email'] is not None:
                handler.addQuickElement(u"email", self.feed['author_email'])
            if self.feed['author_link'] is not None:
                handler.addQuickElement(u"uri", self.feed['author_link'])
            handler.endElement(u"author")
        if self.feed['subtitle'] is not None:
            handler.addQuickElement(u"subtitle", self.feed['subtitle'])
        for cat in self.feed['categories']:
            handler.addQuickElement(u"category", "", {u"term": cat})
        if self.feed['feed_copyright'] is not None:
            handler.addQuickElement(u"rights", self.feed['feed_copyright'])
        self.write_items(handler)
        handler.endElement(u"feed")

    def write_items(self, handler):
        for item in self.items:
            handler.startElement(u"entry", {})
            handler.addQuickElement(u"title", item['title'])
            handler.addQuickElement(u"link", u"", {u"href": item['link'], u"rel": u"alternate"})
            if item['pubdate'] is not None:
                handler.addQuickElement(u"updated", rfc3339_date(item['pubdate']).decode('ascii'))

            # Author information.
            if item['author_name'] is not None:
                handler.startElement(u"author", {})
                handler.addQuickElement(u"name", item['author_name'])
                if item['author_email'] is not None:
                    handler.addQuickElement(u"email", item['author_email'])
                if item['author_link'] is not None:
                    handler.addQuickElement(u"uri", item['author_link'])
                handler.endElement(u"author")

            # Unique ID.
            if item['unique_id'] is not None:
                unique_id = item['unique_id']
            else:
                unique_id = get_tag_uri(item['link'], item['pubdate'])
            handler.addQuickElement(u"id", unique_id)

            # Summary.
            if item['description'] is not None:
                handler.addQuickElement(u"summary", item['description'], {u"type": u"html"})

            # Enclosure.
            if item['enclosure'] is not None:
                handler.addQuickElement(u"link", '',
                    {u"rel": u"enclosure",
                     u"href": item['enclosure'].url,
                     u"length": item['enclosure'].length,
                     u"type": item['enclosure'].mime_type})

            # Categories.
            for cat in item['categories']:
                handler.addQuickElement(u"category", u"", {u"term": cat})

            # Rights.
            if item['item_copyright'] is not None:
                handler.addQuickElement(u"rights", item['item_copyright'])

            handler.endElement(u"entry")


