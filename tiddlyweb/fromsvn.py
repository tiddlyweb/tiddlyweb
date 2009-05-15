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
import urllib2
from urllib2 import urlopen, HTTPError
from urlparse import urljoin

from tiddlyweb.manage import make_command

from tiddlyweb.store import Store
from tiddlyweb.serializer import Serializer
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.importer import handle_tiddler_div


def new_url2pathname(pathname):
    return pathname

urllib2.url2pathname = new_url2pathname


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
    print >> sys.stderr, "handling %s" % url.encode('utf-8')
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
    recipe = recipe.encode('utf-8')
    urls = handle_recipe(url, recipe)
    for url in urls:
        import_one(bag, url)


def handle_recipe(url, content):
    """
    Take a url base and a UTF-8 encoded string and parse it
    as a TiddlyWiki cook recipe.
    """
    rules = [line for line in content.split('\n') if
            line.startswith('tiddler:') or
            line.startswith('plugin:') or
            line.startswith('recipe:')]
    urls = []
    for rule in rules:
        target = rule.split(':', 1)[1]
        target = target.lstrip().rstrip()
        if not '%' in target:
            target = urllib.quote(target)
        target_url = urljoin(url, target)
        urls.append(target_url)
    return urls


def get_url(url):
    """
    Get the content at url, raising HTTPProblem if there is one.
    """
    try:
        print >> sys.stderr, 'getting url: %s' % url.encode('utf-8')
        return _get_url(url)
    except HTTPError, exc:
        print >> sys.stderr, "HTTP Error while getting %s: %s" % (url, exc)
        sys.exit(1)


def _get_url(url):
    """
    Get the content at url, like get_url but without the
    exception handling.
    """
    getter = urlopen(url)
    content = getter.read()
    return unicode(content, 'utf-8')


def import_tid_tiddler(bag, url):
    """
    Import one tiddler, in the tid format, from svn
    url, into bag.
    """
    content = get_url(url)
    tiddler_title = urllib.unquote(url.split('/')[-1])
    tiddler_title = _strip_extension(tiddler_title, '.tid')
    if not type(tiddler_title) == unicode:
        tiddler_title = unicode(tiddler_title, 'utf-8')
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

    If there is no meta file, then set title and tags
    to something appropriate before de-serializing.
    """
    meta_url = '%s.meta' % url
    plugin_content = get_url(url)
    try:
        meta_content = _get_url(meta_url)
    except HTTPError:
        meta_content = 'title: %s\ntags: systemConfig\n' % _strip_extension(url, '.js').split('/')[-1]


    title = [line for line in meta_content.split('\n') if line.startswith('title:')][0]
    title = title.split(':', 1)[1].lstrip().rstrip()
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


def _escape_brackets(content):
    open_pre = content.index('<pre>')
    close_pre = content.rindex('</pre>')
    start = content[0:open_pre+5]
    middle = content[open_pre+5:close_pre]
    end = content[close_pre:]
    middle = middle.replace('>', '&gt;').replace('<', '&lt;')
    return start + middle + end


def _store():
    return Store(config['server_store'][0], {'tiddlyweb.config': config})


def _strip_extension(name, ext):
    """
    Remove trailing extension from name.
    """
    ext_len = len(ext)
    if name[-ext_len:] == ext:
        name = name[:-ext_len]
    return name
