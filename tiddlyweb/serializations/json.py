"""
Text based serializers.
"""

import urllib
import simplejson

from tiddlyweb.serializer import TiddlerFormatError
from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.bag import Policy

class Serialization(SerializationInterface):

    def list_recipes(self, recipes):
        return simplejson.dumps([recipe.name for recipe in recipes])

    def list_bags(self, bags):
        return simplejson.dumps([bag.name for bag in bags])

    def list_tiddlers(self, bag):
        """
        List the tiddlers in a bag as json.
        We will likely want to expand this someday.
        """
        return simplejson.dumps([{'title':tiddler.title, 'revision':tiddler.revision, 'bag':tiddler.bag} for tiddler in bag.list_tiddlers()])

    def recipe_as(self, recipe):
        """
        Recipe as json.
        """
        return simplejson.dumps(recipe)

    def as_recipe(self, recipe, input):
        """
        Turn a json string back into a recipe.
        """
        info = simplejson.loads(input)
        recipe.set_recipe(info)
        return recipe

    def bag_as(self, bag):
        policy = bag.policy
        policy_dict = {}
        for key in ['owner', 'read', 'write', 'create', 'delete', 'manage']:
            policy_dict[key] = getattr(policy, key)
        info = dict(policy=policy_dict)
        return simplejson.dumps(info)

    def as_bag(self, bag, input):
        """
        Turn a JSON string into a bag. This is
        _not_ symetric with bag_as.
        """
        info = simplejson.loads(input)
        if info['policy']:
            bag.policy = Policy()
            for key, value in info['policy'].items():
                bag.policy.__setattr__(key, value)
        return bag

    def tiddler_as(self, tiddler):
        tiddler_dict = {}
        for key in ['title', 'revision', 'modifier', 'created', 'modified', 'tags', 'text', 'bag']:
            tiddler_dict[key] = getattr(tiddler, key, None)

        return simplejson.dumps(tiddler_dict)

    def as_tiddler(self, tiddler, input):
        dict_from_input = simplejson.loads(input)
        for key, value in dict_from_input.iteritems():
            if value:
                setattr(tiddler, key, value)

        return tiddler

