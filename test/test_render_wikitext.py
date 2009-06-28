
from tiddlyweb.model.tiddler import Tiddler

from tiddlyweb.wikitext import render_wikitext

def test_render_wikitext_basic():
    tiddler = Tiddler('foo')
    tiddler.text = '!Hello'

    html = render_wikitext(tiddler, '', {})

    assert '<h1' in html
    assert '</h1>' in html
