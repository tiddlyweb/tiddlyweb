"""
Test GETting a tiddler revision list.
"""


from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2
import simplejson

from fixtures import muchdata, reset_textstore, _teststore


from tiddlyweb.util import sha

text_put_body=u"""modifier: JohnSmith
created: 
modified: 200803030303
tags: [[tag three]]

Hello, I'm John Smith \xbb and I have something to sell.
"""

text_put_body2=u"""modifier: Frank
created: 
modified: 200803030303
tags: [[tag three]]

Hello, I'm John Smith \xbb and I have something to sell.
"""

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

def test_put_tiddler_txt_1():
    http = httplib2.Http()
    encoded_body = text_put_body.encode('utf-8')
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=encoded_body)
    assert response['status'] == '204'

def test_put_tiddler_txt_2():
    http = httplib2.Http()
    encoded_body = text_put_body.encode('utf-8')
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=encoded_body)
    assert response['status'] == '204'

def test_put_tiddler_txt_3():
    http = httplib2.Http()
    encoded_body = text_put_body.encode('utf-8')
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=encoded_body)
    assert response['status'] == '204'
    etag_hash = sha('GUEST:text/plain').hexdigest()
    assert response['etag'] == '"bag1/TestOne/3;%s"' % etag_hash

def test_put_tiddler_txt_4():
    http = httplib2.Http()
    encoded_body = text_put_body2.encode('utf-8')
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=encoded_body)
    assert response['status'] == '204'
    etag_hash = sha('GUEST:text/plain').hexdigest()
    assert response['etag'] == '"bag1/TestOne/4;%s"' % etag_hash

def test_get_tiddler_revision_list():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne/revisions',
            method='GET')

    assert response['status'] == '200'
    assert '3' in content
    assert 'revisions' in content

def test_get_tiddler_revision_1():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne/revisions/1',
            method='GET')
    assert response['status'] == '200'

def test_get_tiddler_revision_2():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne/revisions/2',
            method='GET')
    assert response['status'] == '200'

def test_get_tiddler_revision_3():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne/revisions/3',
            method='GET')
    assert response['status'] == '200'
    etag_hash = sha('GUEST:text/html').hexdigest()
    assert response['etag'] == '"bag1/TestOne/3;%s"' % etag_hash

def test_get_tiddler_revision_5_fail():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne/revisions/5',
            method='GET')
    assert response['status'] == '404'

def test_get_tiddler_revision_nonint_fail():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/TestOne/revisions/four',
            method='GET')
    assert response['status'] == '404'

def test_get_tiddler_revision_list_404():
    """
    Get a 404 when the tiddler doesn't exist.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers/Test99/revisions',
            method='GET')

    assert response['status'] == '404'

def test_get_tiddler_not_revision_list():
    """
    When we retrieve a tiddler list we don't want their revision links.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag1/tiddlers',
            method='GET')

    assert response['status'] == '200'
    assert '3' in content
    assert 'revisions' not in content

def test_get_tiddler_revision_list_json():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/TestOne/revisions.json',
            method='GET')

    info = simplejson.loads(content)
    assert response['status'] == '200'
    assert len(info) == 4

def test_tiddler_revision_list_json_fat():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/TestOne/revisions.json?fat=1',
            method='GET')

    info = simplejson.loads(content)
    assert response['status'] == '200'
    assert len(info) == 4
    assert info[0]['revision'] == 4
    assert info[0]['modifier'] == 'Frank'
    assert info[0]['creator'] == 'JohnSmith'
    assert info[-1]['modifier'] == 'JohnSmith'
    assert info[-1]['creator'] == 'JohnSmith'
    assert 'I have something to sell' in info[0]['text']

    response, resp_content = http.request('http://our_test_domain:8001/bags/bag28/tiddlers/tiddler0/revisions.json',
            method='POST', headers={'if-match': '"bag28/tiddler0/1"', 'content-type': 'text/plain'}, body=content)
    assert response['status'] == '415'
    assert 'application/json required' in resp_content

    response, content = http.request('http://our_test_domain:8001/bags/bag28/tiddlers/tiddler0/revisions.json',
            method='POST', headers={'if-match': '"bag28/tiddler0/1"', 'content-type': 'application/json'}, body=content)

    assert response['status'] == '204'
    assert response['location'] == 'http://our_test_domain:8001/bags/bag28/tiddlers/tiddler0'

    response, content = http.request('http://our_test_domain:8001/bags/bag28/tiddlers/tiddler0/revisions.json',
            method='GET')

    info = simplejson.loads(content)
    assert response['status'] == '200'


def test_etag_generation():
    from tiddlyweb.web.handler.tiddler import _tiddler_etag
    from tiddlyweb.model.bag import Bag
    from tiddlyweb.model.tiddler import Tiddler
    from tiddlyweb.config import config

    tiddler = Tiddler('monkey', 'bar')
    etag = _tiddler_etag({'tiddlyweb.config': config}, tiddler)

    etag_hash = sha(':').hexdigest()
    assert etag == '"bar/monkey/0;%s"' % etag_hash

    bag = Bag('bar')
    store.put(bag)
    store.put(tiddler)
    etag = _tiddler_etag({'tiddlyweb.config': config}, tiddler)
    assert etag == '"bar/monkey/1;%s"' % etag_hash


def test_post_revision_etag_handling():
    # GET a list of revisions
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/long/tiddlers/TestOne/revisions.json?fat=1',
            method='GET')

    json_content = content

    response, content = http.request('http://our_test_domain:8001/bags/bag28/tiddlers/newone/revisions.json',
            method='POST', headers={'content-type': 'application/json'}, body=json_content)

    assert response['status'] == '412'

    response, content = http.request('http://our_test_domain:8001/bags/bag28/tiddlers/newone/revisions.json',
            method='POST', headers={'If-Match': '"bag28/newone/0"', 'content-type': 'application/json'}, body=json_content)

    assert response['status'] == '204'
