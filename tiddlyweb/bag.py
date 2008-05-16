
"""
A Bag is a collection of tiddlers, unique by the title
of the tiddler. A bag can have tiddlers added, removed,
and listed.

At some point the bag will have a security policy and
add and remove will throw permissions exceptions. TBD.
"""

default_policy = "all the world's a stage"

import copy

class Bag(dict):
    """
    XXX: We should subclass for tmpbag and revbag.
    """

    def __init__(self, name, policy=default_policy, tmpbag=False, revbag=False):
        dict.__init__(self)
        self.name = name
        self.policy = policy
        self.tmpbag = tmpbag
        self.revbag = revbag
        self.order = []
        # reference to the store which 'got' us
        # this is can be used in serialization
        self.store = None

    def _tiddler_key(self, tiddler):
        return '%s.%s' % (tiddler.title, tiddler.revision)

    def __getitem__(self, tiddler):
        return dict.__getitem__(self, self._tiddler_key(tiddler) )

    def __setitem__(self, tiddler):
        dict.__setitem__(self, self._tiddler_key(tiddler), tiddler)

    def __delitem__(self, tiddler):
        dict.__delitem__(self, self._tiddler_key(tiddler))

    def add_tiddler(self, tiddler):
        if self.tmpbag:
            pass
        else:
            bags_tiddler = copy.deepcopy(tiddler)
            bags_tiddler.bag = self.name
            tiddler = bags_tiddler
        if self._tiddler_key(tiddler) in self.order:
            self.order.remove(self._tiddler_key(tiddler))
        self.order.append(self._tiddler_key(tiddler))
        self.__setitem__(tiddler)

    def remove_tiddler(self, tiddler):
        if self._tiddler_key(tiddler) in self.order:
            self.order.remove(self._tiddler_key(tiddler))
        self.__delitem__(tiddler)

    def list_tiddlers(self):
        return [self.get(keyword, None) for keyword in self.order]
