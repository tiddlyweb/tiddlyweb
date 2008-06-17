"""
The base Class and interface for Classes
use to get and put data into a storage 
system.
"""

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

    def recipe_get(self, recipe):
        pass

    def recipe_put(self, recipe):
        pass

    def bag_get(self, bag):
        pass

    def bag_put(self, recipe):
        pass

    def tiddler_get(self, tiddler):
        pass

    def tiddler_put(self, tiddler):
        pass

    def user_get(self, user):
        pass

    def user_put(self, user):
        pass

    def list_recipes(self):
        pass

    def list_bags(self):
        pass

    def list_tiddler_revisions(self, tiddler):
        pass
