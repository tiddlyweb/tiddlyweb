"""
The base Class and interface for Classes
use to get and put data into a storage 
system.
"""

from tiddlyweb.store import StoreMethodNotImplemented

class StorageInterface(object):
    """
    A Store is a collection of methods that 
    either store an object or retrieve an object.

    The interface is fairly simple: For the data 
    entities that exist in the TiddlyWeb system there
    (optionally) exists <entity_put and <entity>_get methods
    in each Store.
    
    There are also three supporting methods, list_recipes(),
    list_bags() and list_tiddler_revisions() that provide
    methods for presenting a collection.
    """

    def __init__(self, environ={}):
        self.environ = environ

    def recipe_delete(self, recipe):
        raise StoreMethodNotImplemented

    def recipe_get(self, recipe):
        raise StoreMethodNotImplemented

    def recipe_put(self, recipe):
        raise StoreMethodNotImplemented

    def bag_delete(self, bag):
        raise StoreMethodNotImplemented

    def bag_get(self, bag):
        raise StoreMethodNotImplemented

    def bag_put(self, recipe):
        raise StoreMethodNotImplemented

    def tiddler_delete(self, tiddler):
        raise StoreMethodNotImplemented

    def tiddler_get(self, tiddler):
        raise StoreMethodNotImplemented

    def tiddler_put(self, tiddler):
        raise StoreMethodNotImplemented

    def user_get(self, user):
        raise StoreMethodNotImplemented

    def user_put(self, user):
        raise StoreMethodNotImplemented

    def list_recipes(self):
        raise StoreMethodNotImplemented

    def list_bags(self):
        raise StoreMethodNotImplemented

    def list_tiddler_revisions(self, tiddler):
        raise StoreMethodNotImplemented

    def tiddler_written(self, tiddler):
        """
        Notify the system that a tiddler has been stored.
        This is done to cause search system to update or
        otherwise deal with new content.
        """
        pass

    def search(self, search_query):
        raise StoreMethodNotImplemented
