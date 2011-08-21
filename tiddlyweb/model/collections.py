"""
Collection classes.

These classes are used for containing the other model classes. Because
the main reason for having a collection is to send it out over the web,
the collections keep track of their last-modified time and generate a
hash suitable for use as an ETag.
"""

import logging

from tiddlyweb.store import StoreError
from tiddlyweb.util import sha

from tiddlyweb.model.tiddler import Tiddler


class Collection(object):
    """
    Base class for all collections.

    Can be used directly for general stuff if required.

    A collection acts as generator, yield one of its contents when
    iterated.
    """

    def __init__(self, title=''):
        self._digest = sha()
        self.modified = '0'
        self.title = title
        self.link = ''
        self._container = []

    def __contains__(self, item):
        return item in self._container

    def add(self, thing):
        """
        Add an item to the container, updating
        the digest and modified information.
        """
        self._update_digest(thing)
        self._container.append(thing)
        try:
            modified_string = str(thing.modified)
            modified_string = modified_string.ljust(14, '0')
            if modified_string > self.modified:
                self.modified = modified_string
        except AttributeError:
            pass

    def _update_digest(self, thing):
        """
        Update the digest with this thing.
        """
        self._digest.update(thing)

    def hexdigest(self):
        """
        Return the current hex representation of
        the hash digest of this collection.
        """
        return self._digest.hexdigest()

    def __iter__(self):
        """
        Generate the items in this container.
        """
        for thing in self._container:
            yield thing


class Container(Collection):
    """
    A collection of things which have a name attribute.

    In TiddlyWeb this is for lists of bags and recipes.
    """

    def _update_digest(self, thing):
        """
        Update the digest with this thing.
        """
        self._digest.update(thing.name.encode('utf-8'))


class Tiddlers(Collection):
    """
    A Collection specifically for tiddlers.

    This differs from the base class in two ways:

    The calculation of the digest is more detailed in order to create
    stong ETags for the collection.

    When iterated, if store is set on the Collection, then a yielded
    tiddler will be loaded from the store to fill in all its attributes.
    When a tiddler is added to the collection, if it is already filled,
    a non-full copy is made and put into the collection. This is done
    to save memory and because often the data is not needed.
    """

    def __init__(self, title='', store=None):
        Collection.__init__(self, title)
        self.is_revisions = False
        self.is_search = False
        self.store = store

    def __iter__(self):
        """
        Generate the items in this container.
        Since these are tiddlers, load them if they are
        not loaded. If a tiddler is now gone, skip right
        over that.
        """
        for tiddler in self._container:
            if not tiddler.store and self.store:
                try:
                    tiddler = self.store.get(tiddler)
                except StoreError, exc:
                    logging.debug('missed tiddler in collection: %s, %s',
                            tiddler, exc)
                    continue
            yield tiddler

    def add(self, tiddler):
        """
        Add a reference to the tiddler to the container,
        updating the digest and modified information. If
        the tiddler has recently been deleted, resulting
        in a StoreError, simply don't add it.
        """
        if not tiddler.store and self.store:
            try:
                tiddler = self.store.get(tiddler)
            except StoreError, exc:
                logging.debug(
                        'tried to add missing tiddler to collection: %s, %s',
                        tiddler, exc)
                return
            reference = Tiddler(tiddler.title, tiddler.bag)
            if tiddler.revision:
                reference.revision = tiddler.revision
            if tiddler.recipe:
                reference.recipe = tiddler.recipe
            self._container.append(reference)
        else:
            self._container.append(tiddler)
        self._update_digest(tiddler)
        modified_string = str(tiddler.modified)
        modified_string = modified_string.ljust(14, '0')
        if modified_string > self.modified:
            self.modified = modified_string

    def _update_digest(self, tiddler):
        """
        Update the digest with information from this tiddler.
        """
        try:
            self._digest.update(tiddler.bag.encode('utf-8'))
        except AttributeError:
            pass
        self._digest.update(tiddler.title.encode('utf-8'))
        self._digest.update(str(tiddler.revision))
