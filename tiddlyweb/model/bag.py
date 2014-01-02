"""
A module containing the :py:class:`Bag` class.
"""

from tiddlyweb.model.policy import Policy


class Bag(object):
    """
    A Bag is a virtual container for :py:class:`tiddlers
    <tiddlyweb.model.tiddler.Tiddler>`. The bag provides a domain
    for the tiddlers within identifying those tiddlers uniquely and
    optionally acting a topical, functional or authorization container
    for the tiddlers.

    A bag can contain many tiddlers but every tiddler must have a different
    title. The canonical identifier of a tiddler is the combination of the
    containing bag's name and the tiddler's title.

    Containership is achieved via association: There are no methods on a
    bag to access the contained tiddlers. These are found via
    :py:func:`store.list_bag_tiddlers
    <tiddlyweb.store.Store.list_bag_tiddlers>`.

    A Bag has a :py:class:`Policy <tiddlyweb.model.policy.Policy>`
    which may be used to control access to both the Bag and the tiddlers
    within. These controls are optional and are primarily designed for
    use within the :py:mod:`web handlers <tiddlyweb.web.handler>`.
    """

    def __init__(self, name, desc=u''):
        self.name = name
        self.desc = desc
        self.policy = Policy()  # set to default policy
        self.store = None

    def __repr__(self):
        return '%s:%s' % (self.name, object.__repr__(self))
