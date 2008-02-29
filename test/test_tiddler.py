
"""
Test tiddler, a simple data container for a tiddler.
"""

import sys
sys.path.append('.')
from tiddlyweb.tiddler import Tiddler

test_tiddler_content = "Race car drivers\ngo really very fast."

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
            name = 'test tiddler',
            author = 'test@example.com',
            content = test_tiddler_content,
            tags = ['foo', 'bar']
            )

    assert type(tiddler) == Tiddler, \
            'Tiddler returns a Tiddler'
    assert tiddler.name == 'test tiddler', \
            'tiddler name should be test tiddler, got %s' \
            % tiddler.name
    assert tiddler.author == 'test@example.com', \
            'tiddler author should test@example.com, got %s' \
            % tiddler.author
    assert tiddler.content == test_tiddler_content, \
            'tiddler content is correct'
    assert tiddler.tags == ['foo', 'bar'], \
            'tiddler tags are correct'

