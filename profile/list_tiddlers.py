
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

environ = {}
environ['tiddlyweb.config'] = config

def run():
    clean_store()
    make_tiddlers_for_bag()
    profile_listing_tiddlers()


def clean_store():
    shutil.rmtree('store')

def make_tiddlers_for_bag():
    store = Store('text', environ=environ)

    print 'store', time()
    bag = Bag('profiler')
    store.put(bag)

    for name in range(1, 1000):
        name = str(name)
        tiddler = Tiddler(name, bag.name)
        tiddler.text = name
        store.put(tiddler)

def profile_listing_tiddlers():
    store = Store('text', environ=environ)

    bag = Bag('profiler')
    store.get(bag)

    print 'filter', time()
    #filter_string = '[sort[modified]]'
    filter_string = ''
    tiddlers = control.filter_tiddlers_from_bag(bag, filter_string)

    print 'tmp bag', time()
    tmp_bag = Bag('tmp_bag', tmpbag=True)
    tmp_bag.add_tiddlers(tiddlers)

    #print 'output', time()
    #print ['.' for tiddler in control.get_tiddlers_from_bag(tmp_bag)]

    print 'serializer', time()
    serializer = Serializer('wiki', environ)
    print 'wikify', time()
    output = serializer.list_tiddlers(tmp_bag)

    print 'done', time()


if __name__ == '__main__':
    run()
