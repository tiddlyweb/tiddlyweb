
import simplejson

from tiddlyweb.serializer import Serializer
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag

from tiddlyweb.config import config

from .fixtures import get_store


def test_json_perms():
    store = get_store(config)
    bag = Bag('permstest')
    store.put(bag)
    serializer = Serializer('json', environ={'tiddlyweb.usersign': {
        'name': 'bang', 'roles': []}, 'tiddlyweb.config': config})
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
