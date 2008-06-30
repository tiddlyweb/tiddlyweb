"""
HTML based serializers.
"""

import urllib

from tiddlyweb.serializer import TiddlerFormatError
from tiddlyweb.serializations import SerializationInterface

class Serialization(SerializationInterface):

    def list_recipes(self, recipes):
        """
        List the recipes on the system as html.
        """
        lines = []
        output = '<ul>\n'
        for recipe in recipes:
            line = '<li><a href="recipes/%s">%s</a></li>' % (urllib.quote(recipe.name), recipe.name)
            lines.append(line)
        output += "\n".join(lines)
        return output + '\n</ul>'

    def list_bags(self, bags):
        """
        List the bags on the system as html.
        """
        lines = []
        output = '<ul>\n'
        for bag in bags:
            line = '<li><a href="bags/%s/tiddlers">%s</a></li>' % (urllib.quote(bag.name), bag.name)
            lines.append(line)
        output += "\n".join(lines)
        return output + '\n</ul>'

    def recipe_as(self, recipe):
        """
        Recipe as html.
        """
        lines = []
        for bag, filter in recipe:
            line = '<li><a href="'
            if not isinstance(bag, basestring):
                bag = bag.name
            line += '/bags/%s/tiddlers' % urllib.quote(bag)
            if filter:
                line += '?%s' % urllib.quote(filter)
            line += '">bag: %s filter:%s</a></li>' % (bag, filter)
            lines.append(line)
        output = "\n".join(lines)
        title = 'Bags in Recipe %s' % recipe.name
        tiddler_link = '%s/tiddlers' % urllib.quote(recipe.name)
        return """
<html>
<head><title>%s</title></head>
<body>
<ul>
%s
</ul>
<div><a href="%s">Tiddlers in Recipe</a></div>
</body></html>""" % (title, output, tiddler_link)

    def list_tiddlers(self, bag):
        """
        List the tiddlers in a bag as html.
        """
        lines = []
        for tiddler in bag.list_tiddlers():
            if tiddler.recipe:
                base = 'recipes'
                base_link = urllib.quote(tiddler.recipe)
                wiki_link = '/recipes/%s/tiddlers' % base_link
                title = 'Tiddlers in Recipe %s' % tiddler.recipe
            else:
                base = 'bags'
                base_link = urllib.quote(tiddler.bag)
                wiki_link = '/bags/%s/tiddlers' % base_link
                title = 'Tiddlers in Bag %s' % tiddler.bag
            if bag.revbag:
                line = '<li><a href="/%s/%s/tiddlers/%s/revisions/%s">%s:%s</a></li>' % (base, base_link, urllib.quote(tiddler.title), tiddler.revision, tiddler.title, tiddler.revision)
                wiki_link += '/%s/revisions' % urllib.quote(tiddler.title)
                title = 'Revisions of Tiddler %s' % tiddler.title
            else:
                line = '<li><a href="/%s/%s/tiddlers/%s">%s</a></li>' % (base, base_link, urllib.quote(tiddler.title), tiddler.title)
            lines.append(line)
        if bag.searchbag:
            title = 'Found Tiddlers'
            wiki_link = None
        output = "\n".join(lines)
        return """
%s
<hr>
<ul>
%s
</ul>
</div>
</body></html>""" % (self._tiddler_list_header(title, wiki_link), output)

    def _tiddler_list_header(self, title, wiki_link):
        if wiki_link:
            return"""
<html>
<head><title>%s</title></head>
<body>
<div><a href="%s">These Tiddlers as a TiddlyWiki</a></div>
""" % (title, '%s.wiki' % wiki_link)
        return"""
<html>
<head><title>%s</title></head>
<body>
""" % title

    def tiddler_as(self, tiddler):
        try:
            return self._tiddler_to_wikklyhtml(tiddler)
        except ImportError:
            return self._tiddler_div(tiddler) + '<pre>%s</pre>' % self._html_encode(tiddler.text) + '</div>'

    def _tiddler_div(self, tiddler):
        return u'<div title="%s" server.page.revision="%s" modifier="%s" modified="%s" created="%s" tags="%s">' % \
    (tiddler.title, tiddler.revision, tiddler.modifier, tiddler.modified, tiddler.created, self.tags_as(tiddler.tags))

    def _tiddler_to_html(self, base_url, list_link, tiddler):
        import wikklytext
        def our_resolver(url_fragment, base_url, site_url):
            if '/' in url_fragment:
                return url_fragment, True
            return '%s%s' % (base_url, urllib.quote(url_fragment)), False

        posthook = PostHook()

        link_context = {
                '$BASE_URL': '%s%s' % (base_url, list_link),
                '$REFLOW': 0
                } 
        html, context = wikklytext.WikklyText_to_InnerHTML(
                text=tiddler.text,
                setvars=link_context,
                encoding='utf-8',
                safe_mode=True,
                url_resolver=our_resolver,
                tree_posthook=posthook.treehook
                )
        return html

    def _tiddler_to_wikklyhtml(self, tiddler):
        if tiddler.recipe:
            list_link = 'recipes/%s/tiddlers' % tiddler.recipe
            list_title = 'Recent Changes in Recipe %s' % tiddler.recipe
        else:
            list_link = 'bags/%s/tiddlers' % tiddler.bag
            list_title = 'Recent Changes in Bag %s' % tiddler.bag

        html = self._tiddler_to_html('/', list_link, tiddler)
        return """
<html>
<head><title>%s</title></head>
<body>
<div><a href="%s" title="tiddler list">%s</a></div>
<hr>
%s
%s
</div>
</body></html>
""" % (tiddler.title, urllib.quote('/%s?[sort[-modified]]' % list_link, safe='/?'), list_title, self._tiddler_div(tiddler).encode('utf-8'), html)

class PostHook(object):
    def __init__(self):
        # make map of wikiwords
        self.wikiwords = InfiniteDict()
            
    def treehook(self, rootnode, context):
        from wikklytext.wikwords import wikiwordify
        # add links to any wikiword
        wikiwordify(rootnode, context, self.wikiwords)

class InfiniteDict(dict):
    def __getitem__(self, name):
        return name

    def has_key(self, name):
        return True

