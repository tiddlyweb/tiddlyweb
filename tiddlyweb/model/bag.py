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

    def __init__(self, name, desc=''):
        self.name = unicode(name)
        self.desc = unicode(desc)
        self.policy = Policy() # set to default policy
        self.tiddlers = None
        self.store = None

    def __repr__(self):
        return '%s:%s' % (self.name, object.__repr__(self))
