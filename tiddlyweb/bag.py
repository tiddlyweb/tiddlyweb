
"""
A Bag is a collection of tiddlers, unique by the title
of the tiddler. A bag can have tiddlers added, removed,
and listed.

At some point the bag will have a security policy and
add and remove will throw permissions exceptions. TBD.
"""

default_security_policy = "all the world's a stage"

import copy

class Bag(dict):

    def __init__(self, name, policy=default_security_policy, tmpbag=False):
        dict.__init__(self)
        self.name = name
        self.policy = policy
        self.tmpbag = tmpbag
        self.order = []
        # reference to the store which 'got' us
        # this is can be used in serialization
        self.store = None

    def __getitem__(self, tiddler):
        return dict.__getitem__(self, tiddler.title)

    def __setitem__(self, tiddler):
        dict.__setitem__(self, tiddler.title, tiddler)

    def __delitem__(self, tiddler):
        dict.__delitem__(self, tiddler.title)

    def add_tiddler(self, tiddler):
        if self.tmpbag:
            pass
        else:
            bags_tiddler = copy.deepcopy(tiddler)
            bags_tiddler.bag = self.name
            tiddler = bags_tiddler
        if tiddler.title in self.order:
            self.order.remove(tiddler.title)
        self.order.append(tiddler.title)
        self.__setitem__(tiddler)

    def remove_tiddler(self, tiddler):
        if tiddler.title in self.order:
            self.order.remove(tiddler.title)
        self.__delitem__(tiddler)

    def list_tiddlers(self):
        return [self.get(title, None) for title in self.order]
