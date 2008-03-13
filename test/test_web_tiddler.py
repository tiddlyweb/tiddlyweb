"""
Test that GETting a tiddler in some form.
"""

import sys
sys.path.append('.')

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2

from fixtures import muchdata

from tiddlyweb.store import Store

def setup_module(module):
    from tiddlyweb.web import serve
    # we have to have a function that returns the callable,
    # Selector just _is_ the callable
    def app_fn():
        return serve.load_app('urls.map')
    #wsgi_intercept.debuglevel = 1
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn)

    module.store = Store('text')
    muchdata(module.store)

def test_get_tiddler():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/tiddler8',
            method='GET')

    assert response['status'] == '200', 'response status should be 200'
    assert 'i am tiddler 8' in content, 'tiddler should be correct content, is %s' % content

def test_get_missing_tiddler():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers/tiddler27',
            method='GET')

    assert response['status'] == '404', 'response status should be 404'

