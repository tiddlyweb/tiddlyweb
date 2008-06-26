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

class Serialization(HTMLSerialization):

    def _tiddler_list_header(self, title, wiki_link):
        return"""
<html>
<head>
<title>%s</title>
<link rel="alternate" type="application/atom+xml" title="Atom" href="%s" />
</head>
<body>
<div><a href="%s">These Tiddlers as a TiddlyWiki</a></div>
""" % (title, '%s.atom' % wiki_link, '%s.wiki' % wiki_link)
