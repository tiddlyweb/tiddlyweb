"""
Functions for rendering any :py:class:`tiddler
<tiddlyweb.model.tiddler.Tiddler>` that has been identified as wikitext
into the rendered form (usually HTML) of that wikitext.

Wikitext rendering is engaged when a tiddler is requested via a
``GET``, when the negotiated media-type of the request is html,
and when ``tiddler.type`` is either ``None`` or in the keys of the
dictionary associated with the
:py:mod:`tiddlyweb.config['wikitext.type_render_map'] <tiddlyweb.config>`.

When ``tiddler.type`` is ``None``, the renderer named in
``tiddlyweb.config['wiktext.default_renderer']`` is used. This is
either a module in the :py:mod:`tiddlyweb.wikitext` package,
or a module on ``sys.path``.

When ``tiddler.type`` is something other than ``None``, the renderer is
determined by looking up the type in
``tiddlyweb.config['wikitext.type_render_map']``. The found value is a
module of the same type described above.

The renderer module has a function ``render``.
"""

DEFAULT_RENDERER = 'raw'


def render_wikitext(tiddler=None, environ=None):
    """
    Take a :py:class:`tiddler <tiddlyweb.model.tiddler.Tiddler>`
    and render wikitext in ``tiddler.text`` to some kind of HTML format.
    """
    if environ is None:
        environ = {}
    renderer_name = _determine_renderer(tiddler, environ)
    try:
        imported_module = __import__('tiddlyweb.wikitext.%s' % renderer_name,
                {}, {}, ['render'])
    except ImportError as err:
        err1 = err
        try:
            imported_module = __import__(renderer_name, {}, {}, ['render'])
        except ImportError as err:
            raise ImportError("couldn't load module for %s: %s, %s" %
                    (renderer_name, err, err1))
    return imported_module.render(tiddler, environ)


def _determine_renderer(tiddler, environ):
    """
    Inspect ``tiddlyweb.config`` to determine which wikitext renderer
    should be used for this tiddler.
    """
    config = environ.get('tiddlyweb.config', {})
    try:
        if tiddler.type and tiddler.type != 'None':
            return config['wikitext.type_render_map'][tiddler.type]
    except KeyError:
        pass
    return config.get('wikitext.default_renderer', DEFAULT_RENDERER)
