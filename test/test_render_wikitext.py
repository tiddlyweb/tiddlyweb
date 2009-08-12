
from tiddlyweb.config import config
from tiddlyweb.model.tiddler import Tiddler

from tiddlyweb.wikitext import render_wikitext

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
