"""
Test tiddlyweb.web.query's query_extract, especially
unicode handling.
"""

from tiddlyweb.web.query import Query

import StringIO

def app(environ, start_response):
    pass

def test_operation_simple_get():
    q = Query(app)
    
    environ = {}
    environ['REQUEST_METHOD'] = 'GET'
    environ['QUERY_STRING'] = 'text=hello'

    q.extract_query(environ)
    assert 'text' in environ['tiddlyweb.query']
    assert environ['tiddlyweb.query']['text'][0] == 'hello'

def test_operation_encoded_get():
    q = Query(app)
    
    environ = {}
    environ['REQUEST_METHOD'] = 'GET'
    environ['QUERY_STRING'] = 'text=m%C3%B6ass'

    q.extract_query(environ)
    assert 'text' in environ['tiddlyweb.query']
    assert environ['tiddlyweb.query']['text'][0] == u'm\xf6ass'

def test_operation_simple_post():
    q = Query(app)
    post = StringIO.StringIO()
    post.write('text=m%C3%B6ass')
    post.seek(0)
    environ = {}
    environ['CONTENT_LENGTH'] = 15
    environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
    environ['REQUEST_METHOD'] = 'POST'
    environ['wsgi.input'] = post
    q.extract_query(environ)
    assert 'text' in environ['tiddlyweb.query']
    assert environ['tiddlyweb.query']['text'][0] == u'm\xf6ass'

