"""
Test extracting the QUERY_STRING into tiddlyweb.query.
Not much yet as it is just a directly mappen.
"""


import urllib

from tiddlyweb.web.query import Query

def setup_module(module):
    module.environ = {'QUERY_STRING': 'hello=goodbye&barney=ugly&special=nice', 'REQUEST_METHOD': 'GET'}

def test_interpret_query():
    def app(environ, start_response):
        pass
    query = Query(app)
    query(environ, lambda x: x)
    
    assert environ['tiddlyweb.query']['hello'][0] == 'goodbye'
    assert environ['tiddlyweb.query']['barney'][0] == 'ugly'
    assert environ['tiddlyweb.query']['special'][0] == 'nice'
    assert environ['tiddlyweb.query'].get('flip', [None])[0] == None
