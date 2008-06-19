
from BeautifulSoup import BeautifulSoup

import sys
sys.path.append('.')

import codecs
import simplejson
import httplib2
import re
import urllib

def _html_decode(text):
    return text.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&').replace('&quot;', '"')

def import_wiki(filename='wiki', hostname='localhost', port=8080):
    f = codecs.open(filename, encoding='utf-8')
    wikitext = f.read()
    f.close()

    soup = BeautifulSoup(wikitext)
    store_area = soup.find('div', id='storeArea')
    divs = store_area.findAll('div')

    _do_recipe(hostname, port)
    _do_bag(hostname, port)

    for tiddler in divs:
        _do_tiddler(hostname, port, tiddler)

def _do_recipe(hostname, port):
    json_string = simplejson.dumps([['wiki','']])
    http = httplib2.Http()
    url = 'http://%s:%s/recipes/%s' % (hostname, port, 'wiki')
    response, content = http.request(url, method='PUT', \
            headers={'Content-Type': 'application/json'}, body=json_string)

def _do_bag(hostname, port):
    json_string = simplejson.dumps({'policy': dict(), 'name': 'wiki'})
    http = httplib2.Http()
    url = 'http://%s:%s/bags/%s' % (hostname, port, 'wiki')
    response, content = http.request(url, method='PUT', \
            headers={'Content-Type': 'application/json'}, body=json_string)

def _do_tiddler(hostname, port, tiddler):
    tiddler_dict = {}
    tiddler_dict['title'] = tiddler['title']
    tiddler_dict['text'] = _html_decode(tiddler.find('pre').contents[0])

    for key in (['modifier', 'created', 'modified', 'tags']):
        tiddler_dict[key] = tiddler.get(key, '')

    tiddler_dict['tags'] = _tag_string_to_list(tiddler_dict['tags'])

    json_string = simplejson.dumps(tiddler_dict)

    http = httplib2.Http()
    url = 'http://%s:%s/bags/wiki/tiddlers/%s' % (hostname, port, urllib.quote(tiddler_dict['title']))
    response, content = http.request(url, method='PUT', \
            headers={'Content-Type': 'application/json'}, body=json_string)
    if response['status'] != '204':
        print '%s: %s' % (response['status'], content)
        sys.exit(1)

def _tag_string_to_list(string):
    tags = []
    tag_matcher = re.compile(r'([^ \]\[]+)|(?:\[\[([^\]]+)\]\])')
    for match in tag_matcher.finditer(string):
        if match.group(2):
            tags.append(match.group(2))
        elif match.group(1):
            tags.append(match.group(1))

    return tags

if __name__ == '__main__':
    import_wiki(filename=sys.argv[1], hostname=sys.argv[2], port=sys.argv[3])
