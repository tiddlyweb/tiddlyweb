"""
Functions for rendering anything that has been identified as wikitext
into the rendered form (usually HTML) of that wikitext.

Wikitext rendering is engaged when a tiddler is requested via a
GET, when the negotiated MIME-type of the request is html,
and when tiddler.type is either none or in the keys of the
dictionary associated with the tiddlyweb.config['wikitext.type_render_map'].

When tiddler.type is none, the renderer named in
tiddlyweb.config['wiktext_renderer'] is used. This is either a module
in the tiddlyweb.wikitext package, or a module on sys.path.

When tiddler.type is something other than none, the renderer is
determined by looking up the type in
tiddlyweb.config['wikitext.type_render_map']. The found value is a
module of the same type described above.

The renderer module has a function render.

NOTE: This interface is experimental and subject to change.
"""

DEFAULT_RENDERER = 'raw'


def render_wikitext(tiddler=None, environ=None):
    """
    Take a tiddler and render it's wikitext to some kind
    of HTML format.
    """
    if environ == None:
        environ = {}
    renderer_name = _determine_renderer(tiddler, environ)
    try:
        imported_module = __import__('tiddlyweb.wikitext.%s' % renderer_name,
                {}, {}, ['render'])
    except ImportError, err:
        err1 = err
        try:
            imported_module = __import__(renderer_name, {}, {}, ['render'])
        except ImportError, err:
            raise ImportError("couldn't load module for %s: %s, %s" %
                    (renderer_name, err, err1))
    return imported_module.render(tiddler, environ)


def _determine_renderer(tiddler, environ):
    """
    Inspect tiddlyweb.config to determine which
    wikitext renderer should be used for this
    tiddler.
    """
    config = environ.get('tiddlyweb.config', {})
    try:
        if tiddler.type and tiddler.type != 'None':
            return config['wikitext.type_render_map'][tiddler.type]
    except KeyError:
        pass
    return config.get('wikitext.default_renderer', DEFAULT_RENDERER)
