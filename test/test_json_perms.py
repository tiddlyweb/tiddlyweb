
import simplejson 

from tiddlyweb.serializer import Serializer
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag

from tiddlywebplugins.utils import get_store
from tiddlyweb.config import config


def setup_module(module):
    module.store = get_store(config)

def test_json_perms():
    bag = Bag('permstest')
    store.put(bag)
    serializer = Serializer('json', environ={'tiddlyweb.usersign': {
        'name':'bang', 'roles': []}, 'tiddlyweb.config': config})
    tiddler = Tiddler('permstest', 'permstest')
    tiddler.text = 'permstest'
    store.put(tiddler)
    tiddler.store = store
    serializer.object = tiddler
    string = serializer.to_string()

    info = simplejson.loads(string)

    assert info['title'] == 'permstest'
    assert info['text'] == 'permstest'
    assert info['permissions'] == ['read', 'write', 'create', 'delete']
