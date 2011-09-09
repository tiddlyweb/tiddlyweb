"""
JSON based serializer.
"""

import simplejson

from base64 import b64encode, b64decode

from tiddlyweb.serializer import (TiddlerFormatError, BagFormatError,
        RecipeFormatError)
from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import Policy
from tiddlyweb.util import binary_tiddler, renderable
from tiddlyweb.wikitext import render_wikitext
from tiddlyweb.store import StoreError
from tiddlyweb.web.util import tiddler_url


class Serialization(SerializationInterface):
    """
    Turn various entities to and from JSON.
    """

    def list_recipes(self, recipes):
        """
        Create a JSON list of recipe names from
        the provided recipes.
        """
        return simplejson.dumps([recipe.name for recipe in recipes])

    def list_bags(self, bags):
        """
        Create a JSON list of bag names from the
        provided bags.
        """
        return simplejson.dumps([bag.name for bag in bags])

    def list_tiddlers(self, tiddlers):
        """
        List the tiddlers as JSON.
        The format is a list of dicts in
        the form described by self._tiddler_dict.
        """
        fat = self.environ.get('tiddlyweb.query', {}).get('fat', [False])[0]
        render = self.environ.get('tiddlyweb.query', {}).get('render',
                [False])[0]
        return simplejson.dumps([self._tiddler_dict(tiddler, fat, render) for
            tiddler in tiddlers])

    def recipe_as(self, recipe):
        """
        A recipe as a JSON dictionary.
        """
        policy_dict = dict([(key, getattr(recipe.policy, key)) for
                key in Policy.attributes])
        return simplejson.dumps(dict(desc=recipe.desc, policy=policy_dict,
            recipe=recipe.get_recipe()))

    def as_recipe(self, recipe, input_string):
        """
        Turn a JSON dictionary into a Recipe
        if it is in the proper form. Include
        the policy.
        """
        try:
            info = simplejson.loads(input_string)
        except simplejson.JSONDecodeError, exc:
            raise RecipeFormatError(
                    'unable to make json into recipe: %s, %s'
                    % (recipe.name, exc))
        recipe.set_recipe(info.get('recipe', []))
        recipe.desc = info.get('desc', u'')
        if info.get('policy', {}):
            recipe.policy = Policy()
            for key, value in info['policy'].items():
                recipe.policy.__setattr__(key, value)
        return recipe

    def bag_as(self, bag):
        """
        Create a JSON dictionary representing
        a Bag and Policy.
        """
        policy_dict = dict([(key, getattr(bag.policy, key)) for
                key in Policy.attributes])
        info = dict(policy=policy_dict, desc=bag.desc)
        return simplejson.dumps(info)

    def as_bag(self, bag, input_string):
        """
        Turn a JSON string into a bag.
        """
        try:
            info = simplejson.loads(input_string)
        except simplejson.JSONDecodeError, exc:
            raise BagFormatError(
                    'unable to make json into bag: %s, %s'
                    % (bag.name, exc))

        if info.get('policy', {}):
            bag.policy = Policy()
            for key, value in info['policy'].items():
                bag.policy.__setattr__(key, value)
        bag.desc = info.get('desc', u'')
        return bag

    def tiddler_as(self, tiddler):
        """
        Create a JSON dictionary representing
        a tiddler, as described by _tiddler_dict
        plus the text of the tiddler.
        """
        render = self.environ.get('tiddlyweb.query', {}).get('render',
                [False])[0]
        tiddler_dict = self._tiddler_dict(tiddler, fat=True, render=render)
        return simplejson.dumps(tiddler_dict)

    def as_tiddler(self, tiddler, input_string):
        """
        Turn a JSON dictionary into a Tiddler.
        """
        try:
            dict_from_input = simplejson.loads(input_string)
        except simplejson.JSONDecodeError, exc:
            raise TiddlerFormatError(
                    'unable to make json into tiddler: %s, %s'
                    % (tiddler.title, exc))
        accepted_keys = ['created', 'modified', 'modifier', 'tags', 'fields',
                'text', 'type']
        for key, value in dict_from_input.iteritems():
            if value is not None and key in accepted_keys:
                setattr(tiddler, key, value)
        if binary_tiddler(tiddler):
            try:
                tiddler.text = b64decode(tiddler.text)
            except TypeError, exc:
                raise TiddlerFormatError(
                        'unable to decode expected base64 input in %s: %s'
                        % (tiddler.title, exc))
        return tiddler

    def _tiddler_dict(self, tiddler, fat=False, render=False):
        """
        Select fields from a tiddler to create
        a dictonary.
        """
        unwanted_keys = ['text', 'store']
        wanted_keys = [attribute for attribute in tiddler.slots if
                attribute not in unwanted_keys]
        wanted_info = {}
        for attribute in wanted_keys:
            wanted_info[attribute] = getattr(tiddler, attribute, None)
        wanted_info['permissions'] = self._tiddler_permissions(tiddler)
        wanted_info['uri'] = tiddler_url(self.environ, tiddler)
        if fat:
            if binary_tiddler(tiddler):
                wanted_info['text'] = b64encode(tiddler.text)
            else:
                wanted_info['text'] = tiddler.text
                if render and renderable(tiddler, self.environ):
                    wanted_info['render'] = render_wikitext(tiddler,
                            self.environ)
        return wanted_info

    def _tiddler_permissions(self, tiddler):
        """
        Make a list of the permissions the current user has
        on this tiddler.
        """

        def _read_bag_perms(environ, tiddler):
            """
            Read the permissions for the bag containing
            this tiddler.
            """
            perms = []
            if 'tiddlyweb.usersign' in environ:
                store = tiddler.store
                if store:
                    try:
                        bag = Bag(tiddler.bag)
                        bag = store.get(bag)
                        perms = bag.policy.user_perms(
                                environ['tiddlyweb.usersign'])
                    except StoreError:
                        pass
            return perms

        perms = []
        bag_name = tiddler.bag
        if hasattr(self, '_bag_perms_cache'):
            if bag_name in self._bag_perms_cache:
                perms = self._bag_perms_cache[bag_name]
            else:
                perms = _read_bag_perms(self.environ, tiddler)
        else:
            self._bag_perms_cache = {}
            perms = _read_bag_perms(self.environ, tiddler)
        self._bag_perms_cache[bag_name] = perms
        return perms
