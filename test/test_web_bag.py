"""
Test that GETting a bag can list the tiddlers.
"""


import httplib2
import urllib
import simplejson

from fixtures import muchdata, reset_textstore, _teststore, initialize_app

from tiddlyweb.model.bag import Bag
from tiddlyweb.stores import StorageInterface

policy_dict = dict(
        read=[u'chris',u'jeremy',u'GUEST'],
        write=[u'chris',u'jeremy'],
        create=[u'chris',u'jeremy'],
        delete=[u'chris'],
        manage=[],
        owner=u'chris')

def setup_module(module):
    initialize_app()

    reset_textstore()
    module.store = _teststore()
    muchdata(module.store)

def test_get_bag_tiddler_list_default():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']
    assert content.count('<li>') == 10

def test_get_bag_tiddler_list_404():
    """
    A request for the tiddlers in a non existent bag gives a 404.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag99/tiddlers',
            method='GET')

    assert response['status'] == '404'
    assert '(' not in content

def test_get_bag_tiddler_list_text():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.txt',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/plain; charset=UTF-8', 'response content-type should be text/plain; charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 10, 'len tiddlers should be 10 is %s' % len(content.split('\n'))

def test_get_bag_tiddler_list_html():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.html',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']
    assert content.count('<li>') == 10

def test_get_bag_tiddler_list_415():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.gif',
            method='GET')

    assert response['status'] == '415', 'response status should be 415 is %s' % response['status']

def test_get_bag_tiddler_list_html_default():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers',
            method='GET', headers={'Accept': 'text/html'})

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']
    assert content.count('<li>') == 10

def test_get_bag_tiddler_list_filtered():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.txt?select=title:tiddler8',
            method='GET')

    assert response['status'] == '200'
    assert response['last-modified'] == 'Fri, 23 May 2008 03:03:00 GMT'
    assert len(content.rstrip().split('\n')) == 1, 'len tiddlers should be 1 is %s' % len(content.rstrip().split('\n'))

def test_get_bag_tiddler_list_bogus_filter():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers.txt?sort=-monkey',
            method='GET')

    assert response['status'] == '400'
    assert 'malformed filter' in content

def test_get_bags_default():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']
    assert content.count('<li>') == 30
    assert content.count('bags/') == 30

def test_get_bags_txt():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.txt',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/plain; charset=UTF-8', 'response content-type should be text/plain; charset=UTF-8 is %s' % response['content-type']
    assert len(content.rstrip().split('\n')) == 30, 'len bags should be 32 is %s' % len(content.rstrip().split('\n'))

def test_get_bags_html():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.html',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']
    assert content.count('<li>') == 30
    assert content.count('bags/') == 30

def test_get_bags_unsupported_neg_format():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.gif',
            method='GET')

    assert response['status'] == '415', 'response status should be 415 is %s' % response['status']

def test_get_bags_unsupported_format():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.jpeg',
            method='GET')

    assert response['status'] == '415', 'response status should be 415 is %s' % response['status']

def test_get_bags_json():
    """
    Uses extension.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.json',
            method='GET')

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'application/json; charset=UTF-8', \
            'response content-type should be application/json; charset=UTF-8 is %s' % response['content-type']
    info = simplejson.loads(content)
    assert type(info) == list
    assert len(info) == 30

def test_get_bags_wiki():
    """
    Doesn't support wiki.
    """
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.wiki',
            method='GET')
    assert response['status'] == '415'

def test_get_bags_unsupported_neg_format_with_accept():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags.gif',
            method='GET', headers={'Accept': 'text/html'})

    assert response['status'] == '200', 'response status should be 200 is %s' % response['status']
    assert response['content-type'] == 'text/html; charset=UTF-8', 'response content-type should be text/html;charset=UTF-8 is %s' % response['content-type']

def test_get_bag_tiddler_list_empty():
    """
    A request for the tiddlers in an empty bag gives a 200, empty page.
    """

    bag = Bag('bagempty');
    store.put(bag)

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bagempty/tiddlers.json',
            method='GET')

    assert response['status'] == '200'

    results = simplejson.loads(content)
    assert len(results) == 0

    response, content = http.request('http://our_test_domain:8001/bags/bagempty/tiddlers.html',
            method='GET')

def test_put_bag():
    """
    PUT a new bag to the server.
    """
    json_string = simplejson.dumps(dict(policy=policy_dict))

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bagpuss',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json_string)
    location = response['location']

    assert response['status'] == '204'
    assert location == 'http://our_test_domain:8001/bags/bagpuss'

    response, content = http.request(location, method='GET',
            headers={'Accept': 'application/json'})

    assert response['status'] == '200'
    assert 'etag' in response
    etag = response['etag']
    info = simplejson.loads(content)
    assert info['policy']['delete'] == policy_dict['delete']

    response, content = http.request('http://our_test_domain:8001/bags/bagpuss.json',
            method='GET', headers={'if-none-match': etag})
    assert response['status'] == '304', content

    response, content = http.request('http://our_test_domain:8001/bags/bagpuss.json',
            method='GET', headers={'if-none-match': etag + 'foo'})
    assert response['status'] == '200', content

def test_put_bag_bad_json():
    """
    PUT a new bag to the server.
    """
    json_string = simplejson.dumps(dict(policy=policy_dict))
    json_string = json_string[0:-1]

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bagpuss',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json_string)

    assert response['status'] == '400'
    assert 'unable to put bag' in content
    assert 'unable to make json into' in content

def test_delete_bag():
    """
    PUT a new bag to the server and then DELETE it.
    """
    json_string = simplejson.dumps(dict(policy={}))

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/deleteme',
            method='PUT', headers={'Content-Type': 'application/json'}, body=json_string)
    location = response['location']

    assert response['status'] == '204'
    assert location == 'http://our_test_domain:8001/bags/deleteme'

    response, content = http.request(location, method='DELETE')
    assert response['status'] == '204'

    response, content = http.request(location, method='GET', headers={'Accept':'application/json'})
    assert response['status'] == '404'

def test_put_bag_wrong_type():
    """
    PUT a new bag to the server.
    """
    json_string = simplejson.dumps(dict(policy=policy_dict))

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bagpuss',
            method='PUT', headers={'Content-Type': 'text/plain'}, body=json_string)

    assert response['status'] == '415'

def test_get_bag_tiddlers_constraints():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers',
            method='GET')
    assert response['status'] == '200'

    _put_policy('bag0', dict(policy=dict(read=['NONE'])))
    response, content = http.request('http://our_test_domain:8001/bags/bag0/tiddlers',
            method='GET')
    assert response['status'] == '403'
    assert 'may not read' in content

def test_roundtrip_unicode_bag():
    http = httplib2.Http()
    encoded_bag_name = '%E3%81%86%E3%81%8F%E3%81%99'
    bag_name = urllib.unquote(encoded_bag_name).decode('utf-8')
    bag_content = {'policy':{'read':['a','b','c','GUEST']}}
    body = simplejson.dumps(bag_content)
    response, content = http.request('http://our_test_domain:8001/bags/%s' % encoded_bag_name,
            method='PUT', body=body, headers={'Content-Type': 'application/json'})
    assert response['status'] == '204'

    bag = Bag(bag_name)
    bag = store.get(bag)
    assert bag.name == bag_name

    response, content = http.request('http://our_test_domain:8001/bags/%s.json' % encoded_bag_name,
            method='GET')
    bag_data = simplejson.loads(content)
    assert response['status'] == '200'
    assert bag_data['policy']['read'] == ['a','b','c','GUEST']

def test_no_delete_store():
    """
    XXX: Not sure how to test this. We want to test for
    StoreMethodNotImplemented raising HTTP400. But 
    it is hard to inject in a false store.
    """
    pass


def _put_policy(bag_name, policy_dict):
    """
    XXX: This is duplicated from test_web_tiddler. Clean up!
    """
    json = simplejson.dumps(policy_dict)

    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/%s' % bag_name,
            method='PUT', headers={'Content-Type': 'application/json'}, body=json)
    assert response['status'] == '204'
