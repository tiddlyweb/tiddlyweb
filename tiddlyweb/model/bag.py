"""
A module containing the Bag class.
"""

from tiddlyweb.model.policy import Policy


class Bag(object):
    """
    A Bag is a virtual container for tiddlers. The bag provides a domain
    for the tiddlers within identifying those tiddlers uniquely and
    optionally acting a topical, functional or authorization container
    for the tiddlers.

    A Bag has a Policy (see tiddlyweb.model.policy) which may be used to
    control access to both the Bag and the tiddlers within. These
    controls are optional and are primarily designed for use within the
    web handlers.
    """

    def __init__(self, name, desc=u''):
        self.name = unicode(name)
        self.desc = unicode(desc)
        self.policy = Policy()  # set to default policy
        self.store = None

    def __repr__(self):
        return '%s:%s' % (self.name, object.__repr__(self))
