"""
Collection classes.

These classes are used for containing the other
model classes. Because the main reason for having a
collection is to send it out over the web, the
collections keep track of their last-modified time
and generate a hash suitable for use as an ETag.
"""

from tiddlyweb.util import sha


class Collection(object):
    """
    Base class for all collections.

    Can be used directly for random stuff is required.
    """

    def __init__(self):
        self._digest = sha()
        self.modified = 0
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

    This differs from the base class in how
    the digest is calculated. tiddler.title and
    either tiddler.bag or tiddler.recipe are used.
    """

    def __init__(self):
        Collection.__init__(self)
        self.is_revisions = False
        self.is_search = False

    def _update_digest(self, tiddler):
        """
        Update the digest with information from this tiddler.
        """
        if tiddler.bag:
            container = tiddler.bag
        else:
            container = ''
        self._digest.update(container.encode('utf-8'))
        self._digest.update(tiddler.title.encode('utf-8'))
        self._digest.update(str(tiddler.revision))
