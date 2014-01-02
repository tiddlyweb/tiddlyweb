"""
:py:class:`Serialization <tiddlyweb.serializations.SerializationInterface>`
for HTML.

``HEADER`` and ``FOOTER`` can be overridden to change the basic framing
of the system.
"""

from tiddlyweb import __version__ as VERSION
from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.web.util import encode_name, escape_attribute_value, tiddler_url
from tiddlyweb.wikitext import render_wikitext

from tiddlyweb.fixups import quote


HEADER = u"""<!DOCTYPE HTML>
<html>
<head>
<meta charset="UTF-8">
<title>TiddlyWeb - %(title)s</title>
%(css)s
%(links)s
</head>
<body>
<div id="header">
<h1>%(title)s</h1>
</div>
<div id="content">
"""

FOOTER = u"""
</div>
<div id="footer">
<div id="badge">This is <a href="http://tiddlyweb.com/">TiddlyWeb</a>
%(version)s</div>
<div id="usergreet">User %(username)s.</div>
</div>
</body>
</html>
"""


class Serialization(SerializationInterface):
    """
    Serialize entities and collections to ``HTML`` representations. This
    is primarily used to create browser based presentations. No support
    is provided for turning ``HTML`` into entities.

    Set ``css_uri`` in :py:mod:`config <tiddlyweb.config>` to control
    CSS.

    Set ``tiddlyweb.links`` in ``environ`` to a list of ``<link>``
    elements to include those links in the output.
    """

    def __init__(self, environ=None):
        SerializationInterface.__init__(self, environ)
        self.environ['tiddlyweb.title'] = ''
        self.environ['tiddlyweb.links'] = []

    def list_recipes(self, recipes):
        """
        Yield the provided :py:class:`recipes <tiddlyweb.model.recipe.Recipe>`
        as HTML.
        """
        self.environ['tiddlyweb.title'] = 'Recipes'

        def wrap_list():
            yield self._header()
            yield '<ul id="recipes" class="listing">\n'
            for recipe in recipes:
                yield '<li><a href="recipes/%s">%s</a></li>\n' % (
                        encode_name(recipe.name), recipe.name)
            yield '\n</ul>'
            yield self._footer()

        return wrap_list()

    def list_bags(self, bags):
        """
        Yield the provided :py:class:`bags <tiddlyweb.model.bag.Bag>`
        as HTML.
        """
        self.environ['tiddlyweb.title'] = 'Bags'

        def wrap_list():
            yield self._header()
            yield '<ul id="bags" class="listing">\n'
            for bag in bags:
                yield '<li><a href="bags/%s/tiddlers">%s</a></li>\n' % (
                        encode_name(bag.name), bag.name)
            yield '\n</ul>'
            yield self._footer()

        return wrap_list()

    def list_tiddlers(self, tiddlers):
        """
        Yield the provided :py:class:`tiddlers
        <tiddlyweb.model.tiddler.Tiddler>` as HTML.

        This is somewhat more complex than the other list methods as
        we need to list the tiddler whether it is a revision or not,
        if it is in a bag or recipe or if it is a search result.
        """
        tiddlers.store = None
        title = tiddlers.title
        server_prefix = self._server_prefix()
        lines = []
        container_link = ''

        if tiddlers.link:
            representation_link = tiddlers.link
        elif tiddlers.is_search:
            representation_link = '%s/search' % server_prefix
        else:
            representation_link = ''

        for tiddler in tiddlers:
            if tiddlers.is_revisions:
                line = self._tiddler_revision_info(tiddler)
            else:
                line = self._tiddler_in_container_info(tiddler)
            lines.append(line)

        if not tiddlers.is_revisions and not tiddlers.is_search:
            if tiddlers.bag:
                container_link = ('<div class="baglink">'
                        '<a href="%s/bags/%s">Bag %s</a></div>'
                        % (server_prefix, encode_name(tiddlers.bag),
                            tiddlers.bag))
            elif tiddlers.recipe:
                container_link = ('<div class="recipelink">'
                        '<a href="%s/recipes/%s">Recipe %s</a></div>'
                        % (server_prefix, encode_name(tiddlers.recipe),
                            tiddlers.recipe))

        output = "\n".join(lines)
        self.environ['tiddlyweb.title'] = title

        return """
%s
%s
%s
<ul id="tiddlers" class="listing">
%s
</ul>
%s
""" % (self._header(), self._tiddler_list_header(representation_link),
        container_link, output, self._footer())

    def recipe_as(self, recipe):
        """
        :py:class:`Recipe <tiddlyweb.model.recipe.Recipe>` as HTML,
        including a link to the tiddlers within.
        """
        self.environ['tiddlyweb.title'] = 'Recipe %s' % recipe.name
        lines = []
        for bag, filter_string in recipe.get_recipe():
            line = '<li><a href="'
            line += '%s/bags/%s/tiddlers' % (
                    self._server_prefix(), encode_name(bag))
            if filter_string:
                line += '?%s' % quote(
                        filter_string.encode('utf-8'), safe=':=;')
            line += '">bag: %s filter:%s</a></li>' % (bag, filter_string)
            lines.append(line)
        output = "\n".join(lines)
        tiddler_link = '%s/tiddlers' % encode_name(recipe.name)
        return """
%s
<div class="tiddlerslink"><a href="%s">Tiddlers in Recipe</a></div>
<div id="recipedesc" class="description">%s</div>
<ul id="recipe" class="listing">
%s
</ul>
%s
""" % (self._header(), tiddler_link, recipe.desc, output, self._footer())

    def bag_as(self, bag):
        """
        :py:class:`Bag <tiddlyweb.model.bag.Bag>` as HTML,
        including a link to the tiddlers within.
        """
        self.environ['tiddlyweb.title'] = 'Bag %s' % bag.name
        tiddler_link = '%s/tiddlers' % encode_name(bag.name)
        return """
%s
<div id="bagdesc" class="description">%s</div>
<div class="tiddlerslink"><a href="%s">Tiddlers in Bag %s</a></div>
%s
""" % (self._header(), bag.desc, tiddler_link, bag.name, self._footer())

    def tiddler_as(self, tiddler):
        """
        Transform the provided :py:class:`tiddler
        <tiddlyweb.model.tiddler.Tiddler>` into an HTML representation.
        :py:mod:`Render <tiddlyweb.wikitext>` the ``text`` of the tiddler
        if its ``type`` is configured.
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
        return (self._header() + list_html + self._tiddler_div(tiddler)
                + html + '</div>' + self._footer())

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

    def _tiddler_revision_info(self, tiddler):
        """
        Get the individual revision info for listing revisions.
        """
        if tiddler.recipe:
            base = 'recipes'
        else:
            base = 'bags'
        return ('<li><a href="%s/revisions/%s">%s:%s</a></li>' % (
            tiddler_url(self.environ, tiddler, container=base, full=False),
            tiddler.revision,
            tiddler.title,
            tiddler.revision))

    def _header(self, title=''):
        """
        Return HTML header section.
        """
        css = ''
        css_config = self.environ.get(
                'tiddlyweb.config', {}).get('css_uri', '')
        if css_config:
            css = ('<link rel="stylesheet" href="%s" type="text/css" />' %
                    css_config)
        links = '\n'.join(self.environ.get('tiddlyweb.links', []))
        env_title = self.environ.get('tiddlyweb.title')
        if env_title:
            title = env_title
        template = {
                'title': title,
                'css': css,
                'links': links,
        }
        return HEADER % template

    def _footer(self):
        """
        Return a footer frame for the HTML.
        """
        return FOOTER % {'version': VERSION,
                'username': self.environ.get(
                    'tiddlyweb.usersign', {}).get('name', 'GUEST')}
