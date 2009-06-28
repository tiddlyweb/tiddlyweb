from tiddlyweb.wikklyhtml import wikitext_to_wikklyhtml

def render_wikitext(tiddler=None, path='', environ={}):
    """
    Take a tiddler and render it's wikitext to some kind
    of HTML format.

    container_path is used when generating URLs
    """
    server_prefix = environ.get('tidldyweb.config',
            {}).get('server_prefix', '')
    html = wikitext_to_wikklyhtml('%s/' % server_prefix,
            path, tiddler.text)
    return unicode(html, 'utf-8')


