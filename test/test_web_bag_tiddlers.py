"""
Test posting a wiki to a bag.
"""


from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2
import simplejson

from tiddlyweb.model.bag import Bag
from tiddlyweb.util import sha

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

def test_get_sorted_tiddlers():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.json?sort=title',
            method='GET')
    etag_hash = sha('GUEST:application/json').hexdigest()
    assert response['status'] == '200'
    assert etag_hash in response['etag']
    tiddlers = simplejson.loads(content)
    assert tiddlers[0]['title'] == 'tiddler0'

def test_get_selected_sorted_limited_tiddlers():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.json?select=title:!tiddler1;select=title:!tiddler0;sort=title;limit=1',
            method='GET')
    assert response['status'] == '200'
    tiddlers = simplejson.loads(content)
    assert len(tiddlers) == 1
    assert tiddlers[0]['title'] == 'tiddler2'

def test_not_post_to_bag_tiddlers():
    content = "HI EVERYBODY!"
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/wikibag/tiddlers',
            method='POST', headers={'Content-Type': 'text/x-tiddlywiki'}, body=content)

    assert response['status'] == '405'

