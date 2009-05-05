"""
Experimental diddling around to make sure that
a CGI query string will become what we think it should.

This test file is a playground for the moment.
"""

import pprint

from tiddlyweb.web.query import parse_for_filters

def test_parsing():
    """
    Incomplete testing of parsing the filter string
    as part of the query string parsing, leaving the rest
    of the query string intact.
    """
    string = 'slag=absolute;foo=;select=tag:systemConfig;select=tag:blog;fat=1;sort=-modified;limit=1,10;select=title:monkey'

    environ = {}
    environ['QUERY_STRING'] = string
    environ['tiddlyweb.query'] = {}
    parse_for_filters(environ)

    assert 'tiddlyweb.query' in environ
    assert 'tiddlyweb.filters' in environ
    assert environ['tiddlyweb.filters'][0] == 'select tag:systemConfig'
    assert environ['tiddlyweb.filters'][2] == 'sort -modified'
    assert environ['tiddlyweb.query']['slag'][0] == 'absolute'
