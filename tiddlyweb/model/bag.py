"""
A module containing the Bag class.
"""

from tiddlyweb.model.policy import Policy


class Bag(object):
    """
    A Bag is a virtual container for tiddlers.

    A Bag which has been retrieved from a Store will have
    its 'store' attribute set to the store it was retrieved
    from.

    A Bag has a Policy (see tiddlyweb.model.policy) which may be used
    to control access to both the Bag and the tiddlers within.
    These controls are optional and are primarily designed
    for use within the web handlers.
    """

    def __init__(self, name, desc=''):
        self.name = unicode(name)
        self.desc = unicode(desc)
        self.policy = Policy() # set to default policy
        self.store = None

    def __repr__(self):
        return '%s:%s' % (self.name, object.__repr__(self))
