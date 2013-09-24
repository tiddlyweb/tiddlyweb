"""
Storage systems for TiddlyWeb.

The base class and Interface for classes used to get and put data
into a storage system.
"""

from tiddlyweb.store import StoreMethodNotImplemented


class StorageInterface(object):
    """
    An implementation of the StorageInterface is a collection
    of methods that either store an object or retrieve an object.
    It is not usually access directly but instead called through
    a :py:class:`Store <tiddlyweb.store.Store>` facade.

    The interface is fairly simple: For the data entities that
    exist in the TiddlyWeb system there (optionally) exists
    ``<entity>_put``, ``<entity>_get`` and ``<entity>_delete``
    methods.

    When ``<entity>_get`` is used, an empty object is provided.
    This object is filled by the store method.

    There are also five supporting methods, :py:func:`list_recipes`,
    :py:func:`list_bags`, :py:func:`list_users`,
    :py:func:`list_bag_tiddlers`, and :py:func:`list_tiddler_revisions`
    that provide methods for getting a collection.

    It is useful to understand the classes in the :py:mod:`tiddlyweb.model`
    package when implementing new StorageInterface classes.

    If a method is not implemented by the StorageInterface
    a :py:class:`StoreMethodNotImplemented
    <tiddlyweb.store.StoreMethodNotImplemented>` exception is
    raised and the calling code is expected to handle that intelligently.

    It is somewhat common to not implement :py:func:`list_tiddler_revisions`.
    When this is done it means the instance does not support revisions.
    """

    def __init__(self, store_config=None, environ=None):
        """
        The WSGI environment is made available to the storage system
        so that decisions can be made based on things like the
        request IP. Care should be taken when using ``environ`` related
        data as the environment can change from when a Store is
        instantiated to when it is actually used. Configuration
        information pulled from the store should only be used
        during the initialization phase.
        """
        if environ is None:
            environ = {}
        if store_config is None:
            store_config = {}
        self.environ = environ
        self.store_config = store_config

    def recipe_delete(self, recipe):
        """
        Remove the :py:class:`recipe <tiddlyweb.model.recipe.Recipe>`
        from the store, with no impact on the recipe's :py:class:`tiddlers
        <tiddlyweb.model.tiddler.Tiddler>`.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle deleting recipes')

    def recipe_get(self, recipe):
        """
        Get the indicated :py:class:`recipe <tiddlyweb.model.recipe.Recipe>`
        from the store.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle getting recipes')

    def recipe_put(self, recipe):
        """
        Put :py:class:`recipe <tiddlyweb.model.recipe.Recipe>`
        into the store.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle putting recipes')

    def bag_delete(self, bag):
        """
        Remove :py:class:`bag <tiddlyweb.model.bag.Bag>` from the store,
        *including* the :py:class:`tiddlers <tiddlyweb.model.tiddler.Tiddler>`
        contained by the bag.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle deleting bags')

    def bag_get(self, bag):
        """
        Get the indicated :py:class:`bag <tiddlyweb.model.bag.Bag>`
        from the store.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle getting bags')

    def bag_put(self, bag):
        """
        Put :py:class:`bag <tiddlyweb.model.bag.Bag>` into the store.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle putting bags')

    def tiddler_delete(self, tiddler):
        """
        Delete :py:class:`tiddler <tiddlyweb.model.tiddler.Tiddler>`
        (and all its revisions) from the store.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle deleting tiddlers')

    def tiddler_get(self, tiddler):
        """
        Get a tiddler from the store, returning a populated tiddler
        object. ``tiddler.creator`` and ``tiddler.created`` are based on
        the modifier and modified of the first revision of a tiddler.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle getting tiddlers')

    def tiddler_put(self, tiddler):
        """
        Put :py:class:`tiddler <tiddlyweb.model.tiddler.Tiddler>`
        into the store.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle putting tiddlers')

    def user_delete(self, user):
        """
        Delete :py:class:`user <tiddlyweb.model.user.User>` from the store.

        This will remove the user object but has no impact on other entities
        which may have been modified by the user.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle deleting users')

    def user_get(self, user):
        """
        Get :py:class:`user <tiddlyweb.model.user.User>` from the store.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle getting users')

    def user_put(self, user):
        """
        Put :py:class:`user <tiddlyweb.model.user.User>` into the store.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle putting users')

    def list_recipes(self):
        """
        Retrieve a list of all :py:class:`recipe
        <tiddlyweb.model.recipe.Recipe>` objects in the system.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle listing recipes')

    def list_bags(self):
        """
        Retrieve a list of all :py:class:`bag
        <tiddlyweb.model.bag.Bag>` objects in the system.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle listing bags')

    def list_bag_tiddlers(self, bag):
        """
        Retrieve a list of all :py:class:`tiddler
        <tiddlyweb.model.tiddler.Tiddler>` objects in the named
        :py:class:`bag <tiddlyweb.model.bag.Bag>`.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle listing bag tiddlers')

    def list_users(self):
        """
        Retrieve a list of all :py:class:`user
        <tiddlyweb.model.user.User>` objects in the system.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle listing users')

    def list_tiddler_revisions(self, tiddler):
        """
        Retrieve a list of all the revision identifiers
        for the one :py:class:`tiddler <tiddlyweb.model.tiddler.Tiddler>`.
        """
        raise StoreMethodNotImplemented(
                'this store does not handle listing tiddler revisions')

    def search(self, search_query):
        """
        Search the entire :py:class:`tiddler
        <tiddlyweb.model.tiddler.Tiddler>` store for ``search_query``.

        How search operates is entirely dependent on the StorageInterface
        implementation. The only requirement is that an iterator of
        tiddler objects is returned.
        """
        raise StoreMethodNotImplemented('this store does not provide search')
