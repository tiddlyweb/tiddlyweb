
DEFAULT_RENDERER = 'wikklytextrender'

def render_wikitext(tiddler=None, path='', environ={}):
    """
    Take a tiddler and render it's wikitext to some kind
    of HTML format.

    container_path is used when generating URLs
    """
    renderer_name = _determine_renderer(tiddler, environ)
    try:
        imported_module = __import__('tiddlyweb.wikitext.%s' % renderer_name,
                {}, {}, ['render'])
    except ImportError, err:
        err1 = err
        try:
            imported_module = __import__(renderer, {}, {}, ['render'])
        except ImportError, err:
            raise ImportError("couldn't load module for %s: %s, %s" % (render, err, err1))
    return imported_module.render(tiddler, path, environ)


def _determine_renderer(tiddler, environ):
    return environ.get('tiddlyweb.config', {}).get('wikitext_renderer', DEFAULT_RENDERER)

