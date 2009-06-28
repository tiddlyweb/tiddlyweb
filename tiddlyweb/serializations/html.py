"""
HTML based serializers.
"""

import urllib

from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.web.util import encode_name
from tiddlyweb.wikitext import render_wikitext


class Serialization(SerializationInterface):
    """
    Serialize entities and collections to and from
    HTML representations. This is primarily used
    to create browser based presentations.
    """

    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ
        self.environ['tiddlyweb.title'] = ''
        self.environ['tiddlyweb.links'] = []

    def list_recipes(self, recipes):
        """
        List the recipes on the system as html.
        """
        self.environ['tiddlyweb.title'] = 'Recipes'
        lines = []
        output = '<ul id="recipes" class="listing">\n'
        for recipe in recipes:
            line = '<li><a href="recipes/%s">%s</a></li>' % (
                    encode_name(recipe.name), recipe.name)
            lines.append(line)
        output += "\n".join(lines)
        return output + '\n</ul>'

    def list_bags(self, bags):
        """
        List the bags on the system as html.
        """
        self.environ['tiddlyweb.title'] = 'Bags'
        lines = []
        output = '<ul id="bags" class="listing">\n'
        for bag in bags:
            line = '<li><a href="bags/%s">%s</a></li>' % (
                    encode_name(bag.name), bag.name)
            lines.append(line)
        output += "\n".join(lines)
        return output + '\n</ul>'

    def list_tiddlers(self, bag):
        """
        List the tiddlers in a bag as html.
        """
        server_prefix = self._server_prefix()
        lines = []
        for tiddler in bag.list_tiddlers():
            base, base_link, wiki_link, title = \
                    self._tiddler_list_info(tiddler)
            if bag.revbag:
                line = self._tiddler_revision_info(base, base_link, tiddler)
                wiki_link += '/%s/revisions' % encode_name(tiddler.title)
                title = 'Revisions of Tiddler %s' % tiddler.title
            else:
                line = self._tiddler_in_bag_info(base, base_link, tiddler)
            lines.append(line)

        if bag.searchbag:
            title = 'Found Tiddlers'
            wiki_link = None

        output = "\n".join(lines)
        self.environ['tiddlyweb.title'] = title

        return """
%s
<ul id="tiddlers" class="listing">
%s
</ul>
""" % (self._tiddler_list_header(wiki_link), output)

    def recipe_as(self, recipe):
        """
        Recipe as html.
        """
        self.environ['tiddlyweb.title'] = 'Recipe %s' % recipe.name
        lines = []
        for bag, filter_string in recipe.get_recipe():
            line = '<li><a href="'
            if not isinstance(bag, basestring):
                bag = bag.name
            line += '%s/bags/%s/tiddlers' % (
                    self._server_prefix(), encode_name(bag))
            if filter_string:
                line += '?%s' % urllib.quote(
                        filter_string.encode('utf-8'), safe=':=;')
            line += '">bag: %s filter:%s</a></li>' % (bag, filter_string)
            lines.append(line)
        output = "\n".join(lines)
        title = 'Bags in Recipe %s' % recipe.name
        tiddler_link = '%s/tiddlers' % encode_name(recipe.name)
        return """
<div class="tiddlerslink"><a href="%s">Tiddlers in Recipe</a></div>
<div id="recipedesc" class="description">%s</div>
<ul id="recipe" class="listing">
%s
</ul>
""" % (tiddler_link, recipe.desc, output)

    def bag_as(self, bag):
        """
        Bag as html.
        """
        self.environ['tiddlyweb.title'] = 'Bag %s' % bag.name
        tiddler_link = '%s/tiddlers' % encode_name(bag.name)
        return """
<div id="bagdesc" class="description">%s</div>
<div class="tiddlerslink"><a href="%s">Tiddlers in Bag %s</a></div>
""" % (bag.desc, tiddler_link, bag.name)

    def tiddler_as(self, tiddler):
        """
        Transform the provided tiddler into an HTML
        representation of the tiddler packaged in a
        DIV. If wikklytext is available the wikitext
        will be rendered into formatted HTML.
        """
        if tiddler.recipe:
            list_link = 'recipes/%s/tiddlers' % encode_name(tiddler.recipe)
            list_title = 'Tiddlers in Recipe %s' % tiddler.recipe
        else:
            list_link = 'bags/%s/tiddlers' % encode_name(tiddler.bag)
            list_title = 'Tiddlers in Bag %s' % tiddler.bag
        list_html = ('<div class="tiddlerslink"><a href="%s" ' % list_link +
                'title="tiddler list">%s</a></div>' % list_title)
        html = render_wikitext(tiddler, list_link, self.environ)
        self.environ['tiddlyweb.title'] = tiddler.title
        return list_html + self._tiddler_div(tiddler) + html + '</div>'

    def _server_prefix(self):
        """
        Return the string that is the server prefix,
        for creating URLs.
        """
        config = self.environ.get('tiddlyweb.config', {})
        return config.get('server_prefix', '')

    def _tiddler_div(self, tiddler):
        """
        The string that starts the div that contains a tiddler.
        """
        return u'<div class="tiddler" title="%s" server.page.revision="%s" ' \
                'modifier="%s" modified="%s" created="%s" tags="%s" %s>' % \
                (tiddler.title, tiddler.revision, tiddler.modifier,
                        tiddler.modified, tiddler.created,
                        self.tags_as(tiddler.tags),
                        self._tiddler_fields(tiddler.fields))

    def _tiddler_fields(self, fields):
        """
        Turn tiddler fields into a string suitable for
        _tiddler_div.
        """
        output = []
        for key in fields:
            output.append('%s="%s"' % (key, fields[key]))
        return ' '.join(output)

    def _tiddler_in_bag_info(self, base, base_link, tiddler):
        """
        Get the info for a non-revision tiddler in a list.
        """
        return '<li><a href="%s/%s/%s/tiddlers/%s">%s</a></li>' % (
            self._server_prefix(),
            base,
            base_link,
            encode_name(tiddler.title),
            tiddler.title)

    def _tiddler_list_header(self, wiki_link):
        """
        The string we present at the top of a list of tiddlers.
        """
        if wiki_link:
            return """
<div id="tiddlersheader"><a href="%s">These Tiddlers as a TiddlyWiki</a></div>
""" % ('%s.wiki' % wiki_link)
        return ''

    def _tiddler_list_info(self, tiddler):
        """
        Get the basic link info needed for listing tiddlers.
        """
        if tiddler.recipe:
            base = 'recipes'
            base_link = encode_name(tiddler.recipe)
            wiki_link = '%s/recipes/%s/tiddlers' % (
                    self._server_prefix(), base_link)
            title = 'Tiddlers in Recipe %s' % tiddler.recipe
        else:
            base = 'bags'
            base_link = encode_name(tiddler.bag)
            wiki_link = '%s/bags/%s/tiddlers' % (self._server_prefix(),
                    base_link)
            title = 'Tiddlers in Bag %s' % tiddler.bag
        return base, base_link, wiki_link, title

    def _tiddler_revision_info(self, base, base_link, tiddler):
        """
        Get the individual revision info for listing revisions.
        """
        return  ('<li><a href="%s/%s/%s/tiddlers/'
            '%s/revisions/%s">%s:%s</a></li>' % (
            self._server_prefix(),
            base,
            base_link,
            encode_name(tiddler.title),
            tiddler.revision,
            tiddler.title,
            tiddler.revision))
