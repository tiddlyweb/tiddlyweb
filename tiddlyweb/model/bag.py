"""
A module containing the Bag class.
"""

from tiddlyweb.model.policy import Policy


class Bag(object):
    """
    XXX: Should we subclass for tmpbag and revbag?

    A Bag is a collection of tiddlers.
    A bag can have tiddlers added, removed, and listed.

    A Bag which has been retrieved from a Store will have
    its 'store' attribute set to the store it was retrieved
    from. This makes it possible to later lazily load the
    tiddlers that are in the bag.

    A Bag has a Policy (see tiddlyweb.model.policy) which may be used
    to control access to both the Bag and the tiddlers within.
    These controls are optional and are primarily designed
    for use within the web handlers.
    """

    def __init__(self, name, desc='',
            tmpbag=False, revbag=False, searchbag=False):
        self.name = unicode(name)
        self.desc = unicode(desc)
        self.policy = Policy() # set to default policy
        self.tmpbag = tmpbag
        self.revbag = revbag
        self._tiddlers = []
        self.searchbag = searchbag
        self.store = None

    def __repr__(self):
        return '%s:%s' % (self.name, object.__repr__(self))

    def _tiddler_copy(self, tiddler):
        """
        Set the bag attribute on a non tmpbag tiddler to this bag's name.
        """
        if self.tmpbag:
            pass
        else:
            tiddler.bag = self.name
        return tiddler

    def add_tiddler(self, tiddler):
        """
        Inject a tiddler into the bag. Depending on the
        type of bag in use, this may or may not clobber
        a tiddler of the same name in the bag.
        """
        tiddler = self._tiddler_copy(tiddler)
        self._tiddlers.append(tiddler)

    def add_tiddlers(self, tiddlers):
        """
        Call add_tiddler() on a list of tiddlers.
        For convenience.
        """
        for tiddler in tiddlers:
            self.add_tiddler(tiddler)

    def gen_tiddlers(self):
        """
        Make a generator of all the tiddlers in the bag,
        in the order they were added.
        """
        return (tiddler for tiddler in self._tiddlers)

    def list_tiddlers(self):
        """
        List all the tiddlers in the bag, in the order
        they were added.
        """
        return self._tiddlers
