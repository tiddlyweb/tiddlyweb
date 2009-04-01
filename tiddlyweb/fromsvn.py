"""
A built-in twanager plugin for retrieving tiddlers, plugins or full
recipes from the TiddlyWiki subversion repository. Provide the name of
one bag and one or more http or file urls on the twanager command line.

Example:

   twanager from_svn bag0 http://tiddly-svn.dyndns.org/Trunk/verticals/stunplugged/index.html.recipe

If the url is a recipe it will be parsed for lines beginning with
recipe: or tiddler.

If recipe, that recipe is retrieved and recursively parsed.

If tiddler, if the end of the URL is js, then get the .js and .js.meta
files, massage them, join them together, make a tiddler, and put it in
the store.

Otherwise assume we have a tiddler in the <div> format and use importer
code to import it.
"""

import sys

import html5lib
from html5lib import treebuilders

import urllib
from urllib2 import urlopen, HTTPError
from urlparse import urljoin

from tiddlyweb.manage import make_command

from tiddlyweb.store import Store
from tiddlyweb.serializer import Serializer
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.importer import handle_tiddler_div


@make_command()
def from_svn(args):
    """Import one or more plugins, tiddlers or recipes in cook format: <bag> <http or file URL>"""
    bag = args[0]
    urls = args[1:]
    if not bag or not urls:
        raise IndexError('missing args')
    import_list(bag, urls)


def import_list(bag, urls):
    """Import a list of svn urls into bag."""
    for url in urls:
        import_one(bag, url)


def import_one(bag, url):
    """Import one svn url into bag."""
    print >> sys.stderr, "handling %s" % url
    if url.endswith('.recipe'):
        import_via_recipe(bag, url)
    elif url.endswith('.js'):
        import_plugin(bag, url)
    elif url.endswith('.tid'):
        import_tid_tiddler(bag, url)
    else:
        import_tiddler(bag, url)


def import_via_recipe(bag, url):
    """
    Import one recipe, at svn url, into bag, calling import_one as needed.
    Will recurse recipes as it finds them. NO LOOP DETECTION.
    """
    recipe = get_url(url)
    rules = [line for line in recipe.split('\n') if line.startswith('tiddler:') or line.startswith('recipe:')]
    for rule in rules:
        target = rule.split(':', 2)[1]
        target = target.lstrip().rstrip()
        target_url = urljoin(url, target)
        import_one(bag, target_url)


def get_url(url):
    """
    Get the content at url, raising HTTPProblem if there is one.
    """
    try:
        getter = urlopen(url)
        content = getter.read()
        return unicode(content, 'utf-8')
    except HTTPError, exc:
        print >> sys.stderr, "HTTP Error while getting %s: %s" % (url, exc)
        sys.exit(1)


def import_tid_tiddler(bag, url):
    """
    Import one tiddler, in the tid format, from svn
    url, into bag.
    """
    content = get_url(url)
    tiddler_title = unicode(urllib.unquote(url.split('/')[-1].rstrip('.tid')), 'UTF-8')
    tiddler = Tiddler(tiddler_title, bag)
    tiddler = process_tid_tiddler(tiddler, content)
    _store().put(tiddler)


def process_tid_tiddler(tiddler, content):
    """
    Deserialize a tid.
    """
    serializer = Serializer('text')
    serializer.object = tiddler
    serializer.from_string(content)
    return tiddler


def import_tiddler(bag, url):
    """
    Import one tiddler, at svn url, into bag.
    """
    content = get_url(url)
    tiddler = process_tiddler(content)
    handle_tiddler_div(bag, tiddler, _store())


def process_tiddler(content):
    """
    Turn some content into a div element representing
    a tiddler.
    """
    content = _escape_brackets(content)
    parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('beautifulsoup'))
    soup = parser.parse(content)
    tiddler = soup.find('div')
    return tiddler


def import_plugin(bag, url):
    """
    Import one plugin, at svn url, into bag, retrieving
    both the .js and .js.meta files.
    """
    meta_url = '%s.meta' % url
    plugin_content = get_url(url)
    meta_content = get_url(meta_url)

    title = [line for line in meta_content.split('\n') if line.startswith('title:')][0]
    title = title.split(':', 2)[1].lstrip().rstrip()
    tiddler_meta = '\n'.join([line for line in meta_content.split('\n') if not line.startswith('title:')])

    tiddler_meta.rstrip()
    tiddler_text = '%s\n\n%s' % (tiddler_meta, plugin_content)

    tiddler = Tiddler(title, bag)
    serializer = Serializer('text')
    serializer.object = tiddler
    serializer.from_string(tiddler_text)

    _store().put(tiddler)


def init(config_in):
    """Register the config into the plugin."""
    global config
    config = config_in


def _store():
    return Store(config['server_store'][0], {'tiddlyweb.config': config})


def _escape_brackets(content):
    open_pre = content.index('<pre>')
    close_pre = content.rindex('</pre>')
    start = content[0:open_pre+5]
    middle = content[open_pre+5:close_pre]
    end = content[close_pre:]
    middle = middle.replace('>', '&gt;').replace('<', '&lt;')
    return start + middle + end
