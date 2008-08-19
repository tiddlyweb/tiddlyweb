"""
A StorageInterface that stores in Google Data.
"""

import logging

from google.appengine.ext import db
from google.appengine.api import memcache

from tiddlyweb.bag import Bag, Policy
from tiddlyweb.recipe import Recipe
from tiddlyweb.tiddler import Tiddler
from tiddlyweb.serializer import Serializer
from tiddlyweb.store import NoBagError, NoRecipeError, NoTiddlerError, NoUserError, StoreLockError
from tiddlyweb.stores import StorageInterface

class GDRecipe(db.Model):
    name = db.StringProperty(required=True)
    recipe = db.ListProperty(unicode)

class GDBag(db.Model):
    name = db.StringProperty(required=True)
    desc = db.StringProperty()
    tiddlers = db.ListProperty(unicode)

class GDTiddler(db.Model):
    title = db.StringProperty(required=True)
    modifier = db.StringProperty()
    modified = db.StringProperty()
    created = db.StringProperty()
    tags = db.ListProperty(unicode)
    text = db.TextProperty()
    bag = db.StringProperty()

class Store(StorageInterface):

    def _recipe_key(self, name):
        return 'key:recipe:%s' % name

    def _bag_key(self, name):
        return 'key:bag:%s' % name

    def _tiddler_key(self, tiddler):
        return 'key:tiddler:%s:%s' % (tiddler.bag, tiddler.title)

    def recipe_get(self, recipe):
        gdrecipe = GDRecipe.get_by_key_name(self._recipe_key(recipe.name))

        if not gdrecipe:
            raise NoRecipeError
        
        recipe_list = []
        for line in gdrecipe.recipe:
            bag, filter = line.split('?')
            recipe_list.append([bag, filter])

        recipe.set_recipe(recipe_list)
        return recipe

    def recipe_put(self, recipe):
        gdrecipe = GDRecipe(key_name=self._recipe_key(recipe.name), name=recipe.name)
        recipe_list = []
        for bag, filter in recipe.get_recipe():
            line = '%s?%s' % (bag, filter)
            recipe_list.append(line)
        gdrecipe.recipe = recipe_list
        gdrecipe.put()

    def bag_get(self, bag):
        try:
            mem_bag = memcache.get(self._bag_key(bag.name))
            if mem_bag is not None:
                for tiddler_title in mem_bag.tiddlers:
                    bag.add_tiddler(Tiddler(tiddler_title))
                bag.desc = mem_bag.desc
                return bag
            logging.info('memcache miss on bag %s' % bag.name)
        except KeyError:
            pass

        gdbag = GDBag.get_by_key_name(self._bag_key(bag.name))

        if not gdbag:
            raise NoBagError

        bag_tiddler_query = GDTiddler.gql('WHERE bag = :1')
        bag_tiddler_query.bind(bag.name)
        
        bags_tiddlers = []
        bag.desc = gdbag.desc
        for gdtiddler in bag_tiddler_query:
            tiddler = Tiddler(gdtiddler.title)
            bag.add_tiddler(tiddler)
            bags_tiddlers.append(tiddler.title)

# ignore policy for now, use the default

        gdbag.tiddlers = bags_tiddlers
        memcache.add(self._bag_key(bag.name), gdbag)
        return bag

    def bag_put(self, bag):
        gdbag = GDBag(key_name=self._bag_key(bag.name), name=bag.name)
        gdbag.tiddlers = [tiddler.title for tiddler in bag.list_tiddlers()]
        gdbag.put()
        memcache.set(self._bag_key(bag.name), gdbag)

    def tiddler_delete(self, tiddler):
        gdtiddler = GDTiddler.get_by_key_name(self._tiddler_key(tiddler))

        if not gdtiddler:
            raise NoTiddlerError, 'tiddler %s not found' % (tiddler.title)

        logging.info('deleting tiddler %s so trashing bag cache at %s' % (tiddler.title, tiddler.bag))
        memcache.delete(self._bag_key(tiddler.bag))
        memcache.delete(self._tiddler_key(tiddler))
        gdtiddler.delete()

    def tiddler_get(self, tiddler):
        try:
            mem_tiddler = memcache.get(self._tiddler_key(tiddler))
            if mem_tiddler is not None:
                for item in ['text', 'bag', 'modifier', 'modified', 'created', 'tags']:
                    tiddler.__setattr__(item, mem_tiddler.__getattribute__(item))
                return tiddler
        except KeyError:
            pass

        logging.warning('memcache miss on tiddler %s' % tiddler.title)
        gdtiddler = GDTiddler.get_by_key_name(self._tiddler_key(tiddler))

        if not gdtiddler:
            raise NoTiddlerError, 'tiddler %s not found' % (tiddler.title)

        # be explicit for now
        tiddler.modifier = gdtiddler.modifier
        tiddler.modified = gdtiddler.modified
        tiddler.created = gdtiddler.created
        tiddler.text = gdtiddler.text
        tiddler.tags = gdtiddler.tags
        tiddler.bag = gdtiddler.bag

        memcache.add(self._tiddler_key(tiddler), gdtiddler)
        return tiddler

    def tiddler_put(self, tiddler):
        gdtiddler = GDTiddler(key_name=self._tiddler_key(tiddler), title=tiddler.title, bag=tiddler.bag)
        gdtiddler.modifier = tiddler.modifier
        gdtiddler.modified = tiddler.modified
        gdtiddler.created = tiddler.created
        gdtiddler.text = tiddler.text
        gdtiddler.tags = tiddler.tags
        gdtiddler.put()
        memcache.delete(self._bag_key(tiddler.bag))
        memcache.delete(self._tiddler_key(tiddler))

    def user_get(self, user):
        pass

    def user_put(self, user):
        pass

    def list_recipes(self):
        q = GDRecipe.all()

        recipes = []
        try:
            for gdrecipe in q:
                recipe = Recipe(gdrecipe.name)
                recipe_list = []
                for line in gdrecipe.recipe:
                    bag, filter = line.split('?')
                    recipe_list.append([bag, filter])
                recipe.set_recipe(recipe_list)
                recipes.append(recipe)
        except TypeError:
            pass

        return recipes

    def list_bags(self):
        q = GDBag.all()

        try:
            return [Bag(bag.name) for bag in q]
        except TypeError:
            return []

