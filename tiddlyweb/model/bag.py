"""
A module containing the Bag class.
"""

import copy

from tiddlyweb.model.policy import Policy


class Bag(object):
    """
    XXX: Should we subclass for tmpbag and revbag?

    A Bag is an ordered collection of tiddlers in a similar
    authorization and topic domain.

    A bag provides a generator for the tiddlers within.

    A Bag which has been retrieved from a Store will have
    its 'store' attribute set to the store it was retrieved
    from. This makes it possible to later lazily load the
    tiddlers that are in the bag.

    A Bag has a Policy (see tiddlyweb.policy) which may be used
    to control access to both the Bag and the tiddlers within.
    These controls are optional and are primarily designed
    for use within the web handlers.
    """

    def __init__(self, name, desc='', searchbag=False, revbag=False, source=None):
        self.name = unicode(name)
        self.revbag = revbag
        self.searchbag = searchbag
        self.desc = unicode(desc)
        self.policy = Policy() # set to default policy
        self.store = None
        self.sources = []
        self.listed = []
        self.tiddlers = None
        self.add_tiddler_source(source)

    def add_tiddler_source(self, source):
        if source:
            self.sources.append(source)
            if self.tiddlers == None:
                self.tiddlers = self._make_tiddler_lister()

    def _make_tiddler_lister(self):
        for source in self.sources:
            for tiddler in source:
                try:
                    if not tiddler.bag:
                        tiddler.bag = self.name
                except AttributeError:
                    pass
                self.listed.append(tiddler)
                yield tiddler

    def __repr__(self):
        return self.name + object.__repr__(self)

    def add_tiddler(self, tiddler):
        self.add_tiddler_source(tid for tid in [tiddler])

    def add_tiddlers(self, tiddlers):
        """
        Call add_tiddler() on an iter of tiddlers.
        For convenience.
        """
        self.add_tiddler_source(tiddler for tiddler in tiddlers)

    def list_tiddlers(self):
        """
        List all the tiddlers in the bag, in the order
        they were added.
        """
        tiddlers = list(self.tiddlers)
        if tiddlers:
            print 'returning gen list'
            return tiddlers
        else:
            print 'returning list'
            return self.listed
