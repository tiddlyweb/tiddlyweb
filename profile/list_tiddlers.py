
import sys
sys.path.insert(0, '.')

import shutil

from time import time

from tiddlyweb.config import config

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import Store
from tiddlyweb import control
from tiddlyweb.serializer import Serializer
from tiddlyweb.filters import parse_for_filters

environ = {}
environ['tiddlyweb.config'] = config

def run():
    clean_store()
    make_tiddlers_for_bag()
    profile_listing_tiddlers()


def clean_store():
    try:
        shutil.rmtree('store')
    except OSError:
        pass

def make_tiddlers_for_bag():
    store = Store('text', environ=environ)

    print 'store', time()
    bag = Bag('profiler')
    store.put(bag)

    for name in range(1, 10000):
        tag = name % 10
        name = str(name)
        tag = str(tag)
        tiddler = Tiddler(name, bag.name)
        tiddler.text = name
        tiddler.tags.append(tag)
        store.put(tiddler)
    print 'stored', time()

def profile_listing_tiddlers():
    store = Store('text', environ=environ)
    environ['tiddlyweb.store'] = store

    bag = Bag('profiler')
    bag.skinny = True
    store.get(bag)

    print 'filter', time()
    filter_string = 'select=tag:100'
    filters, leftovers = parse_for_filters(filter_string, environ)
    tiddlers = control.filter_tiddlers_from_bag(bag, filters)

    print 'tmp bag', time()
    tmp_bag = Bag('tmp_bag', tmpbag=True)
    tmp_bag.add_tiddlers(tiddlers)

    print 'output', time()
    print [tiddler.title for tiddler in control.get_tiddlers_from_bag(tmp_bag)]

    #print 'serializer', time()
    #serializer = Serializer('wiki', environ)
    #print 'wikify', time()
    #output = serializer.list_tiddlers(tmp_bag)

    print 'done', time()


if __name__ == '__main__':
    command = sys.argv[1]
    print command
    if command == 'clean':
        clean_store()
    elif command == 'make':
        make_tiddlers_for_bag()
    elif command == 'filter':
        profile_listing_tiddlers()
    else:
        run()
