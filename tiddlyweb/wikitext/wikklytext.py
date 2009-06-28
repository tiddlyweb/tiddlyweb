from tiddlyweb.wikklyhtml import wikitext_to_wikklyhtml

def render(tiddler, path, environ):
    server_prefix = environ.get('tidldyweb.config',
            {}).get('server_prefix', '')
    html = wikitext_to_wikklyhtml('%s/' % server_prefix,
            path, tiddler.text)
    return unicode(html, 'utf-8')

