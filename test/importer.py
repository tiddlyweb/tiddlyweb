
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

def import_wiki(filename='wiki'):
    f = codecs.open(filename, encoding='utf-8')
    wikitext = f.read()
    f.close()

    soup = BeautifulSoup(wikitext)
    store_area = soup.find('div', id='storeArea')
    divs = store_area.findAll('div')

    _do_recipe()
    _do_bag()

    for tiddler in divs:
        _do_tiddler(tiddler)

def _do_recipe():
    json_string = simplejson.dumps([['wiki','']])
    http = httplib2.Http()
    url = 'http://localhost:8080/recipes/%s' % 'wiki'
    response, content = http.request(url, method='PUT', \
            headers={'Content-Type': 'application/json'}, body=json_string)

def _do_bag():
    json_string = simplejson.dumps({'policy': dict(), 'name': 'wiki'})
    http = httplib2.Http()
    url = 'http://localhost:8080/bags/%s' % 'wiki'
    response, content = http.request(url, method='PUT', \
            headers={'Content-Type': 'application/json'}, body=json_string)

def _do_tiddler(tiddler):
    tiddler_dict = {}
    tiddler_dict['title'] = tiddler['title']
    tiddler_dict['text'] = _html_decode(tiddler.find('pre').contents[0])

    for key in (['modifier', 'created', 'modified', 'tags']):
        tiddler_dict[key] = tiddler.get(key, '')

    tiddler_dict['tags'] = _tag_string_to_list(tiddler_dict['tags'])

    json_string = simplejson.dumps(tiddler_dict)

    http = httplib2.Http()
    url = 'http://localhost:8080/bags/wiki/tiddlers/%s' % urllib.quote(tiddler_dict['title'])
    response, content = http.request(url, method='PUT', \
            headers={'Content-Type': 'application/json'}, body=json_string)
    if response['status'] != '204':
        print '%s: %s' % (response['status'], content)

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
    import_wiki()
