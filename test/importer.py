
from BeautifulSoup import BeautifulSoup

import sys
sys.path.append('.')

import codecs
import simplejson
import httplib2
import re

from tiddlyweb.store import Store
from tiddlyweb.serializer import Serializer, TiddlerFormatError
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.recipe import Recipe
from tiddlyweb.bag import Bag

def import_wiki(filename='wiki'):
    f = codecs.open(filename, encoding='utf-8')
    wikitext = f.read()
    f.close()

    store = Store('text')

    soup = BeautifulSoup(wikitext)
    store_area = soup.find('div', id='storeArea')
    divs = store_area.findAll('div')

    _do_recipe(store)
    _do_bag(store)

    for tiddler in divs:
        _do_tiddler(store, tiddler)

def _do_recipe(store):
    recipe = Recipe('wiki')
    recipe.set_recipe([['wiki', '']])
    store.put(recipe)

def _do_bag(store):
    bag = Bag('wiki')
    store.put(bag)

def _do_tiddler(store, tiddler):
    tiddler_dict = {}
    tiddler_dict['title'] = tiddler['title']
    tiddler_dict['text'] = tiddler.find('pre').contents[0]
    for key in (['modifier', 'created', 'modified', 'tags']):
        tiddler_dict[key] = tiddler.get(key, '')

    tiddler_dict['tags'] = _tag_string_to_list(tiddler_dict['tags'])

    json_string = simplejson.dumps(tiddler_dict)

    http = httplib2.Http()
    url = 'http://localhost:8080/bags/wiki/tiddlers/%s' % tiddler_dict['title']
    print 'js: %s\nu: %s' % (json_string, url)
    response, content = http.request(url, method='PUT', \
            headers={'Content-Type': 'application/json'}, body=json_string)

    print '%s, %s' % (tiddler_dict['title'], response['status'])

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
