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

from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.serializations.html import Serialization as HTMLSerialization
from tiddlyweb.web.util import tiddler_url

class Serialization(HTMLSerialization):

    def _tiddler_list_header(self, wiki_link):
        if wiki_link:
            self.environ['tiddlyweb.links'].append(
                    '<link rel="alternate" type="application/atom+xml" title="Atom" href="%s" />' \
                            % '%s.atom' % wiki_link
                    )
        return HTMLSerialization._tiddler_list_header(self, wiki_link)

    def tiddler_as(self, tiddler):
        self.environ['tiddlyweb.links'].append(
                    '<link rel="alternate" type="application/atom+xml" title="Atom" href="%s" />' \
                            % '%s.atom' % tiddler_url(self.environ, tiddler)
                            )
        return HTMLSerialization.tiddler_as(self, tiddler)



