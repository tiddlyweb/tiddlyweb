
from BeautifulSoup import BeautifulSoup

import sys
sys.path.append('.')

import codecs

from tiddlyweb.store import Store
from tiddlyweb.serializer import Serializer, TiddlerFormatError
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.recipe import Recipe
from tiddlyweb.bag import Bag

def import_wiki(filename='wiki'):
    f = codecs.open(filename, encoding='utf-8')
    wikitext = f.read()

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
    title = tiddler['title']
    contents = tiddler.find('pre').contents[0]
    tiddler_string = "modifier: %s\ncreated: %s\nmodified: %s\ntags: %s\n\n%s" % \
            (tiddler.get('modifier', ''), tiddler.get('created', ''), \
            tiddler.get('modified', ''), tiddler.get('tags', ''), contents)
    new_tiddler = Tiddler(title)
    new_tiddler.bag = 'wiki'
    serializer = Serializer('text')
    serializer.object = new_tiddler
    serializer.from_string(tiddler_string)
    try:
        store.put(new_tiddler)
    except UnicodeEncodeError, e:
        raise Exception, 'tiddler %s caused unicode encode error: %s' % (new_tiddler.title, e)

if __name__ == '__main__':
    import_wiki()
