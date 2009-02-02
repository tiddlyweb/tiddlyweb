"""
A module containing the Bag class.
"""

import copy

from tiddlyweb.model.policy import Policy


class Bag(dict):
    """
    XXX: Should we subclass for tmpbag and revbag?

    A Bag is a collection of tiddlers, usually unique by
    the title of the tiddler. A bag can have tiddlers added, removed,
    and listed.

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
        self.name = name
        self.desc = desc
        self.policy = Policy() # set to default policy
        self.tmpbag = tmpbag
        self.revbag = revbag
        self.searchbag = searchbag
        self.order = []
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
        If a bag is not a tmpbag, when we put a tiddler in
        it, we need to copy the tiddler, otherwise operations
        that happen to the tiddler in the bag may impact a
        tiddler somewhere else in the process space.
        """
        if self.tmpbag:
            pass
        else:
            bags_tiddler = copy.deepcopy(tiddler)
            bags_tiddler.bag = self.name
            tiddler = bags_tiddler
        return tiddler

    def __getitem__(self, tiddler):
        return dict.__getitem__(self, self._tiddler_key(tiddler))

    def __setitem__(self, tiddler):
        dict.__setitem__(self, self._tiddler_key(tiddler), tiddler)

    def __delitem__(self, tiddler):
        dict.__delitem__(self, self._tiddler_key(tiddler))

    def add_tiddler(self, tiddler):
        """
        Inject a tiddler into the bag. Depending on the
        type of bag in use, this may or may not clobber
        a tiddler of the same name in the bag.
        """
        tiddler = self._tiddler_copy(tiddler)
        if self._tiddler_key(tiddler) in self.order:
            self.order.remove(self._tiddler_key(tiddler))
        self.order.append(self._tiddler_key(tiddler))
        self.__setitem__(tiddler)

    def add_tiddlers(self, tiddlers):
        """
        Call add_tiddler() on a list of tiddlers.
        For convenience.
        """
        for tiddler in tiddlers:
            self.add_tiddler(tiddler)

    def remove_tiddler(self, tiddler):
        """
        Remove the provided tiddler from the bag.
        """
        if self._tiddler_key(tiddler) in self.order:
            self.order.remove(self._tiddler_key(tiddler))
        self.__delitem__(tiddler)

    def list_tiddlers(self):
        """
        List all the tiddlers in the bag, in the order
        they were added.
        """
        return [self.get(keyword, None) for keyword in self.order]
