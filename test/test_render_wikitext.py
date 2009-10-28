
from tiddlyweb.config import config
from tiddlyweb.model.tiddler import Tiddler

from tiddlyweb.wikitext import render_wikitext

import py

def setup_module(module):
    tiddler = Tiddler('foo')
    tiddler.text = '!Hello'
    module.tiddler = tiddler


def test_render_wikitext_plain():
    renderer = config['wikitext.default_renderer']
    config['wikitext.default_renderer'] = 'raw'
    text = render_wikitext(tiddler, {'tiddlyweb.config': config})
    config['wikitext.default_renderer'] = renderer

    assert '<h1' not in text
    assert '<pre>' in text

def test_render_no_config():
    text = render_wikitext(tiddler)
    assert '<pre>' in text
    assert '!Hello' in text

def test_renderer_not_found():
    renderer = config['wikitext.default_renderer']
    config['wikitext.default_renderer'] = 'monkey'
    py.test.raises(ImportError, 'render_wikitext(tiddler, {"tiddlyweb.config":config})')
    config['wikitext.default_renderer'] = renderer

def test_renderer_type_not_found_does_raw():
    tiddler.type = 'fake/type'
    text = render_wikitext(tiddler)
    assert '!Hello' in text

def test_renderer_type_found_no_import():
    tiddler.type = 'image/gif'
    config['wikitext.type_render_map'][tiddler.type] = 'monkey'
    py.test.raises(ImportError, 'render_wikitext(tiddler, {"tiddlyweb.config":config})')
