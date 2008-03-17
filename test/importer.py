
from BeautifulSoup import BeautifulSoup

import sys
sys.path.append('.')

from tiddlyweb.store import Store
from tiddlyweb.serializer import Serializer, TiddlerFormatError
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.recipe import Recipe
from tiddlyweb.bag import Bag

def import_wiki(filename='wiki'):
    f = open(filename)
    wikitext = f.read()

    store = Store('text')

    soup = BeautifulSoup(wikitext)
    store_area = soup.find('div', id='storeArea')
    divs = store_area.findAll('div')

    recipe = Recipe('wiki')
    recipe.set_recipe([['wiki', '']])
    store.put(recipe)

    bag = Bag('wiki')
    store.put(bag)

    for tiddler in divs:
        title = tiddler['title']
        contents = tiddler.find('pre').contents[0]
        try:
            tag_string = tiddler['tags']
        except KeyError:
            tag_string = ''
        tiddler_string = "modifier: importer\ntags: %s\n\n%s" % (tag_string, contents)
        new_tiddler = Tiddler(title)
        new_tiddler.bag = 'wiki'
        serializer = Serializer('text')
        serializer.object = new_tiddler
        serializer.from_string(tiddler_string)
        try:
            store.put(new_tiddler)
        except UnicodeEncodeError:
            pass
        if title == 'faq':
            print new_tiddler.title
            print new_tiddler.content

if __name__ == '__main__':
    import_wiki()
