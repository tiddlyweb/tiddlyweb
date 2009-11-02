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

    filters, leftovers = parse_for_filters(string)

    assert len(filters) == 5
    assert leftovers == 'slag=absolute;foo=;fat=1'

    text_filters = []
    for filter, text, environ in filters:
        text_filters.append(text)
    assert len(text_filters) == 5
    assert text_filters[0][1] == 'tag:systemConfig'
    assert text_filters[1][1] == 'tag:blog'
    assert text_filters[2][1] == '-modified'
    assert text_filters[3][1] == '0,10'

    tiddlers = [Tiddler('a'), Tiddler('monkey')]
    tiddlers[1].tags = ['systemConfig', 'blog']
    tiddlers = list(recursive_filter(filters, tiddlers))
    
    assert len(tiddlers) == 1
    assert tiddlers[0].title == 'monkey'
