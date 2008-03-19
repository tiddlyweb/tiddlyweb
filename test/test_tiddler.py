
"""
Test tiddler, a simple data container for a tiddler.
"""

import sys
sys.path.append('.')
from tiddlyweb.tiddler import Tiddler

test_tiddler_text = "Race car drivers\ngo really very fast."

def setup_module(module):
    pass

def test_tiddler_create():
    tiddler = Tiddler()

    assert type(tiddler) == Tiddler, 'Tiddler returns a Tiddler, %s, %s' % (type(tiddler), Tiddler)

def test_tiddler_full_create():
    """
    Confirm we can populate a tiddler at create time.
    """

    tiddler = Tiddler(
            title = 'test tiddler',
            modifier = 'test@example.com',
            text = test_tiddler_text,
            tags = ['foo', 'bar'],
            bag = 'bagone'
            )

    assert type(tiddler) == Tiddler, \
            'Tiddler returns a Tiddler'
    assert tiddler.title == 'test tiddler', \
            'tiddler title should be test tiddler, got %s' \
            % tiddler.title
    assert tiddler.modifier == 'test@example.com', \
            'tiddler modifier should test@example.com, got %s' \
            % tiddler.modifier
    assert tiddler.text == test_tiddler_text, \
            'tiddler content is correct'
    assert tiddler.tags == ['foo', 'bar'], \
            'tiddler tags are correct'
    assert tiddler.bag == 'bagone', \
            'tiddler has a bag of bagone'

