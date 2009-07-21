"""
Test search via the web.
"""


from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2
import simplejson

from fixtures import muchdata, reset_textstore, _teststore

def setup_module(module):
    from tiddlyweb.web import serve
    # we have to have a function that returns the callable,
    # Selector just _is_ the callable
    def app_fn():
        return serve.load_app()
    #wsgi_intercept.debuglevel = 1
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn)

    reset_textstore()
    module.store = _teststore()
    muchdata(module.store)

def test_simple_search():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/search?q=tiddler%200',
            method='GET')

    assert response['status'] == '200'

def test_title_search():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/search?q=tiddler0',
            method='GET')

    assert response['status'] == '200'

def test_malformed_search():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/search',
            method='GET')

    assert response['status'] == '400'

def test_json_search():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/search.json?q=tiddler%200',
            method='GET')

    assert response['status'] == '200'
    assert 'json' in response['content-type']
    info = simplejson.loads(content)
    assert len(info) == 30

def test_json_search_filtered():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/search.json?q=tiddler%200;select=tag:tagtwo',
            method='GET')

    assert response['status'] == '200'
    assert 'json' in response['content-type']
    info = simplejson.loads(content)
    assert len(info) == 30
