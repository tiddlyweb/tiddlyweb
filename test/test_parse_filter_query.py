"""
Experimental diddling around to make sure that
a CGI query string will become what we think it should.

This test file is a playground for the moment.
"""

from tiddlyweb.web.query import parse_for_filters
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.filters import recursive_filter

def test_parsing():
    """
    Incomplete testing of parsing the filter string
    as part of the query string parsing, leaving the rest
    of the query string intact.
    """
    string = 'slag=absolute;foo=;select=tag:systemConfig;select=tag:blog;fat=1;sort=-modified;limit=0,10;select=title:monkey'

    environ = {}
    environ['QUERY_STRING'] = string
    environ['tiddlyweb.query'] = {}
    parse_for_filters(environ)

    assert 'tiddlyweb.query' in environ
    assert 'tiddlyweb.filters' in environ
    assert len(environ['tiddlyweb.filters']) == 5
    assert environ['tiddlyweb.query']['slag'][0] == 'absolute'

    filters = environ['tiddlyweb.filters']

    tiddlers = [Tiddler('a'), Tiddler('monkey')]
    tiddlers[1].tags = ['systemConfig', 'blog']
    tiddlers = recursive_filter(filters, tiddlers)
    
    assert len(tiddlers) == 1
    assert tiddlers[0].title == 'monkey'
