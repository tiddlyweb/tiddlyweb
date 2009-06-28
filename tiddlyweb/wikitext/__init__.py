
DEFAULT_RENDERER = 'wikklytext'

def render_wikitext(tiddler=None, path='', environ={}):
    """
    Take a tiddler and render it's wikitext to some kind
    of HTML format.

    container_path is used when generating URLs
    """
    renderer_name = environ.get('tiddlyweb.config', {}).get('wikitext_renderer', DEFAULT_RENDERER)
    imported_module = __import__('tiddlyweb.wikitext.%s' % renderer_name, {}, {}, ['render'])
    return imported_module.render(tiddler, path, environ)


