"""
Render TiddlyWiki syntax wikitext to HTML
using the WikklyText enginge.
"""

import wikklytext
import urllib

from tiddlyweb.web.util import encode_name


def render(tiddler, environ):
    """
    Render TiddlyWiki wikitext in the provided
    tiddler to HTML. The provided path helps
    set paths in wikilinks correctly.
    """
    server_prefix = environ.get('tidldyweb.config',
            {}).get('server_prefix', '')
    if tiddler.recipe:
        path = 'recipes/%s/tiddlers' % encode_name(tiddler.recipe)
    elif tiddler.bag:
        path = 'bags/%s/tiddlers' % encode_name(tiddler.bag)
    else:
        path = ''
    html = wikitext_to_wikklyhtml('%s/' % server_prefix,
            path, tiddler.text)
    return unicode(html, 'utf-8')


def wikitext_to_wikklyhtml(base_url, path_url, wikitext):
    """
    Turn a wikitext into HTML.
    base_url: starting url for links in the wikitext (e.g. '/')
    path_url: path from base to wikitext (e.g. 'recipes/foorecipe/tiddlers')
    """

    def our_resolver(url_fragment, base_url, site_url):
        """
        Turn url information for a wikiword into a link.
        """
        if '://' in url_fragment or url_fragment.startswith('/'):
            return url_fragment, True
        return '%s%s' % (base_url, urllib.quote(url_fragment, safe='')), False

    posthook = PostHook()

    link_context = {
            '$BASE_URL': '%s%s' % (base_url, path_url),
            '$REFLOW': 0}
    html, context = wikklytext.WikklyText_to_InnerHTML(
            text=wikitext,
            setvars=link_context,
            encoding='utf-8',
            safe_mode=True,
            url_resolver=our_resolver,
            tree_posthook=posthook.treehook)
    return html


class PostHook(object):
    """
    After we transform the wikitext into a
    tree with need to link up the wiki words.
    """

    def __init__(self):
        # make map of wikiwords
        self.wikiwords = InfiniteDict()

    def treehook(self, rootnode, context):
        """
        Turn wikiwords into links.
        """
        from wikklytext.wikwords import wikiwordify
        # add links to any wikiword
        wikiwordify(rootnode, context, self.wikiwords)


class InfiniteDict(dict):
    """
    Model a dictionary that returns
    true for any key.
    """

    def __getitem__(self, name):
        return name

    def has_key(self, name):
        """
        This is an infiniate dict. It has all keys.
        """
        return True
