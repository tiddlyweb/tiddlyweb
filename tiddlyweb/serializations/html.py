"""
HTML based serializers.
"""

import urllib

from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.web.util import encode_name, escape_attribute_value, tiddler_url
from tiddlyweb.wikitext import render_wikitext


class Serialization(SerializationInterface):
    """
    Serialize entities and collections to and from
    HTML representations. This is primarily used
    to create browser based presentations.
    """

    def __init__(self, environ=None):
        SerializationInterface.__init__(self, environ)
        self.environ['tiddlyweb.title'] = ''
        self.environ['tiddlyweb.links'] = []

    def list_recipes(self, recipes):
        """
        List the recipes on the system as html.
        """
        self.environ['tiddlyweb.title'] = 'Recipes'

        def wrap_list():
            yield '<ul id="recipes" class="listing">\n'
            for recipe in recipes:
                yield '<li><a href="recipes/%s">%s</a></li>\n' % (
                        encode_name(recipe.name), recipe.name)
            yield '\n</ul>'

        return wrap_list()

    def list_bags(self, bags):
        """
        List the bags on the system as html.
        """
        self.environ['tiddlyweb.title'] = 'Bags'

        def wrap_list():
            yield '<ul id="bags" class="listing">\n'
            for bag in bags:
                yield '<li><a href="bags/%s/tiddlers">%s</a></li>\n' % (
                        encode_name(bag.name), bag.name)
            yield '\n</ul>'

        return wrap_list()

    def list_tiddlers(self, tiddlers):
        """
        List the tiddlers as html.
        """
        tiddlers.store = None
        title = tiddlers.title
        server_prefix = self._server_prefix()
        lines = []
        representation_link = tiddlers.link
        bag_link = ''
        for tiddler in tiddlers:
            if not representation_link:
                representation_link = self._tiddler_list_info(tiddler)
            if tiddlers.is_revisions:
                line = self._tiddler_revision_info(tiddler)
            else:
                line = self._tiddler_in_container_info(tiddler)
            lines.append(line)

        if tiddlers.is_search:
            representation_link = '%s/search' % server_prefix

        try:
            routing_args = self.environ.get('wsgiorg.routing_args')[1]
        except (TypeError, IndexError, KeyError):
            routing_args = {}

        if 'bag_name' in routing_args and not 'tiddler_name' in routing_args:
            bag_name = routing_args['bag_name']
            bag_name = urllib.unquote(bag_name)
            bag_name = unicode(bag_name, 'utf-8')
            bag_link = ('<div class="baglink"><a href="%s/bags/%s">'
                    'Bag %s</a></div>' % (server_prefix,
                        encode_name(bag_name), bag_name))

        output = "\n".join(lines)
        self.environ['tiddlyweb.title'] = title

        return """
%s
%s
<ul id="tiddlers" class="listing">
%s
</ul>
""" % (self._tiddler_list_header(representation_link), bag_link, output)

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
        DIV. Render the content using the render_wikitext
        subsystem.
        """
        if tiddler.recipe:
            list_link = 'recipes/%s/tiddlers' % encode_name(tiddler.recipe)
            list_title = 'Tiddlers in Recipe %s' % tiddler.recipe
        else:
            list_link = 'bags/%s/tiddlers' % encode_name(tiddler.bag)
            list_title = 'Tiddlers in Bag %s' % tiddler.bag
        list_html = ('<div class="tiddlerslink"><a href="%s/%s" ' %
                (self._server_prefix(), list_link) +
                'title="tiddler list">%s</a></div>' % list_title)
        html = render_wikitext(tiddler, self.environ)
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
        return u"""
<div class="tiddler" title="%s" server.page.revision="%s"
     modifier="%s" creator="%s" modified="%s" created="%s" tags="%s" %s>
 """ % (escape_attribute_value(tiddler.title),
         tiddler.revision,
         escape_attribute_value(tiddler.modifier),
         escape_attribute_value(tiddler.creator),
         tiddler.modified,
         tiddler.created,
         escape_attribute_value(self.tags_as(tiddler.tags)),
         self._tiddler_fields(tiddler.fields))

    def _tiddler_fields(self, fields):
        """
        Turn tiddler fields into a string suitable for
        _tiddler_div.
        """
        output = []
        for key, val in fields.items():
            output.append('%s="%s"' % (key, escape_attribute_value(val)))
        return ' '.join(output)

    def _tiddler_in_container_info(self, tiddler):
        """
        Get the info for a non-revision tiddler in a list.
        """
        if tiddler.recipe:
            base = 'recipes'
        else:
            base = 'bags'
        return '<li><a href="%s">%s</a></li>' % (
            tiddler_url(self.environ, tiddler, container=base, full=False),
            tiddler.title.replace(' ', '&nbsp;', 1))

    def _tiddler_list_header(self, representation_link):
        """
        The string we present at the top of a list of tiddlers.
        """
        if representation_link:
            extension_types = self.environ.get('tiddlyweb.config',
                    {}).get('extension_types', {}).keys()
            links = []
            query_string = self.environ.get('QUERY_STRING', '')
            if query_string:
                query_string = '?%s' % query_string
            for extension in extension_types:
                link = '<a href="%s.%s%s">%s</a>' % (representation_link,
                        extension, query_string, extension)
                links.append(link)
            link_info = ' '.join(links)
            return """
<div id="tiddlersheader">This list of tiddlers as: %s</div>
""" % (link_info)
        return ''

    def _tiddler_list_info(self, tiddler):
        """
        Get the basic link info needed for listing tiddlers.
        """
        if tiddler.recipe:
            representation_link = '%s/recipes/%s/tiddlers' % (
                    self._server_prefix(), encode_name(tiddler.recipe))
        else:
            representation_link = '%s/bags/%s/tiddlers' % (
                    self._server_prefix(), encode_name(tiddler.bag))
        return representation_link

    def _tiddler_revision_info(self, tiddler):
        """
        Get the individual revision info for listing revisions.
        """
        if tiddler.recipe:
            base = 'recipes'
        else:
            base = 'bags'
        return  ('<li><a href="%s/revisions/%s">%s:%s</a></li>' % (
            tiddler_url(self.environ, tiddler, container=base, full=False),
            tiddler.revision,
            tiddler.title,
            tiddler.revision))
