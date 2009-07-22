"""
A module containing the Bag class.
"""

import copy

from tiddlyweb.model.policy import Policy


class Bag(dict):
    """
    XXX: Should we subclass for tmpbag and revbag?

    A Bag is an ordered collection of tiddlers in a similar
    authorization and topic domain.

    A bag acts as a generator.

    A Bag which has been retrieved from a Store will have
    its 'store' attribute set to the store it was retrieved
    from. This makes it possible to later lazily load the
    tiddlers that are in the bag.

    A Bag has a Policy (see tiddlyweb.policy) which may be used
    to control access to both the Bag and the tiddlers within.
    These controls are optional and are primarily designed
    for use within the web handlers.
    """

    def __init__(self, name, desc='',
            tmpbag=False, revbag=False, searchbag=False):
        dict.__init__(self)
        self.name = unicode(name)
        self.desc = unicode(desc)
        self.policy = Policy() # set to default policy
        self.tmpbag = tmpbag
        self.revbag = revbag
        self.order = []
        self.searchbag = searchbag
        self.store = None

    def _tiddler_key(self, tiddler):
        """
        Calculate the dict key for indexing this tiddler
        in the bag. If we are a searchbag we need to include bag.
        If we are a revbag we need to include revision. Otherwise
        we just want to use the tiddler.title (so that clobbering
        happens).
        """
        if self.searchbag:
            return '%s.%s.%s' % (tiddler.bag, tiddler.title, tiddler.revision)
        if self.revbag:
            return '%s.%s' % (tiddler.title, tiddler.revision)
        return '%s' % (tiddler.title)

    def _tiddler_copy(self, tiddler):
        """
        If a bag is not a tmpbag, add a bag attribute.
        """
        if self.tmpbag:
            pass
        else:
            tiddler.bag = self.name
        return tiddler

    def __repr__(self):
        return self.name + object.__repr__(self)

    def __getitem__(self, tiddler):
        return dict.__getitem__(self, self._tiddler_key(tiddler))

    def __setitem__(self, key, tiddler):
        dict.__setitem__(self, key, tiddler)

    def __delitem__(self, tiddler):
        dict.__delitem__(self, self._tiddler_key(tiddler))

    def add_tiddler(self, tiddler):
        """
        Inject a tiddler into the bag. Depending on the
        type of bag in use, this may or may not clobber
        a tiddler of the same name in the bag.
        """
        tiddler = self._tiddler_copy(tiddler)
        tiddler_key = self._tiddler_key(tiddler)
        try:
            self.order.remove(tiddler_key)
        except ValueError:
            pass
        self.order.append(tiddler_key)
        self.__setitem__(self._tiddler_key(tiddler), tiddler)

    def add_tiddlers(self, tiddlers):
        """
        Call add_tiddler() on a list of tiddlers.
        For convenience.
        """
        [self.add_tiddler(tiddler) for tiddler in tiddlers]

    def gen_tiddlers(self):
        """
        Make a generator of all the tiddlers in the bag, 
        in the order they were added.
        """
        try:
            return self.tiddler_generator
        except AttributeError:
            return (self.get(keyword, None) for keyword in self.order)

    def list_tiddlers(self):
        """
        List all the tiddlers in the bag, in the order
        they were added.
        """
        try:
            return [tiddler for tiddler in self.tiddler_generator]
        except AttributeError:
            return [self.get(keyword, None) for keyword in self.order]
