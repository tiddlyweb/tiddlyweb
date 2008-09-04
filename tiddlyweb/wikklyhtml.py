
import wikklytext
import urllib

def wikitext_to_wikklyhtml(base_url, path_url, wikitext):
    """
    Turn a wikitext into HTML.
    base_url: starting url for links in the wikitext (e.g. '/')
    path_url: path from base to wikitext (e.g. 'recipes/foorecipe/tiddlers')
    """
    
    def our_resolver(url_fragment, base_url, site_url):
        if '/' in url_fragment:
            return url_fragment, True
        return '%s%s' % (base_url, urllib.quote(url_fragment)), False

    posthook = PostHook()

    link_context = {
            '$BASE_URL': '%s%s' % (base_url, path_url),
            '$REFLOW': 0
            } 
    html, context = wikklytext.WikklyText_to_InnerHTML(
            text=wikitext,
            setvars=link_context,
            encoding='utf-8',
            safe_mode=True,
            url_resolver=our_resolver,
            tree_posthook=posthook.treehook
            )
    return html

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

