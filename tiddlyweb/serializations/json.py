"""
:py:class:`Serialization <tiddlyweb.serializations.SerializationInterface>`
for ``JSON``.
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
    Turn entities and collections thereof to and from ``JSON``.
    """

    def list_recipes(self, recipes):
        """
        Create a ``JSON`` list of :py:class:`recipe
        <tiddlyweb.model.recipe.Recipe>` names from the provided ``recipes``.
        """
        return simplejson.dumps([recipe.name for recipe in recipes])

    def list_bags(self, bags):
        """
        Create a ``JSON`` list of :py:class:`bag <tiddlyweb.model.bag.Bag>`
        names from the provided ``bags``.
        """
        return simplejson.dumps([bag.name for bag in bags])

    def list_tiddlers(self, tiddlers):
        """
        List the provided :py:class:`tiddlers
        <tiddlyweb.model.tiddler.Tiddler>` as ``JSON``. The format is a
        list of dicts in the form described by :py:func:`_tiddler_dict`.

        If ``fat=1`` is set in ``tiddlyweb.query`` include the ``text``
        of each tiddler in the output.

        If ``render=1`` is set in ``tiddlyweb.query`` include the
        :py:mod:`rendering <tiddlyweb.wikitext>` of the ``text``
        of each tiddler in the output, if the tiddler is renderable.
        """
        query = self.environ.get('tiddlyweb.query', {})
        fat = 0
        render = 0
        try:
            fat = int(query.get('fat', [fat])[0])
            render = int(query.get('render', [render])[0])
        except ValueError:
            pass

        return simplejson.dumps([self._tiddler_dict(tiddler, fat, render) for
            tiddler in tiddlers])

    def recipe_as(self, recipe):
        """
        A :py:class:`recipe <tiddlyweb.model.recipe.Recipe>` as a
        ``JSON`` dictionary. Includes the recipe's :py:class:`policy
        <tiddlyweb.model.policy.Policy>`.
        """
        policy_dict = dict([(key, getattr(recipe.policy, key)) for
                key in Policy.attributes])
        return simplejson.dumps(dict(desc=recipe.desc, policy=policy_dict,
            recipe=recipe.get_recipe()))

    def as_recipe(self, recipe, input_string):
        """
        Turn a ``JSON`` dictionary into a :py:class:`recipe
        <tiddlyweb.model.recipe.Recipe>` if it is in the proper form.
        Include the :py:class:`policy <tiddlyweb.model.policy.Policy>`.
        """
        try:
            info = simplejson.loads(input_string)
        except simplejson.JSONDecodeError as exc:
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
        A :py:class:`bag <tiddlyweb.model.bag.Bag>` as a
        ``JSON`` dictionary. Includes the bag's :py:class:`policy
        <tiddlyweb.model.policy.Policy>`.
        """
        policy_dict = dict([(key, getattr(bag.policy, key)) for
                key in Policy.attributes])
        info = dict(policy=policy_dict, desc=bag.desc)
        return simplejson.dumps(info)

    def as_bag(self, bag, input_string):
        """
        Turn a ``JSON`` dictionary into a :py:class:`bag
        <tiddlyweb.model.bag.Bag>` if it is in the proper form.
        Include the :py:class:`policy <tiddlyweb.model.policy.Policy>`.
        """
        try:
            info = simplejson.loads(input_string)
        except simplejson.JSONDecodeError as exc:
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
        Create a ``JSON`` dictionary representing a tiddler, as described by
        :py:func:`_tiddler_dict` plus the ``text`` of the tiddler.

        If ``fat=0`` is set in ``tiddlyweb.query`` do not include the
        ``text`` of the tiddler in the output.

        If ``render=1`` is set in ``tiddlyweb.query`` include the
        :py:mod:`rendering <tiddlyweb.wikitext>` of the ``text``
        of the tiddler in the output, if the tiddler is renderable.
        """
        query = self.environ.get('tiddlyweb.query', {})
        fat = 1
        render = 0
        try:
            fat = int(query.get('fat', [fat])[0])
            render = int(query.get('render', [render])[0])
        except ValueError:
            pass

        tiddler_dict = self._tiddler_dict(tiddler, fat=fat, render=render)
        return simplejson.dumps(tiddler_dict)

    def as_tiddler(self, tiddler, input_string):
        """
        Turn a ``JSON`` dictionary into a :py:class:`tiddler
        <tiddlyweb.model.tiddler.Tiddler>`. Any keys in the ``JSON``
        which are not recognized will be ignored.
        """
        try:
            dict_from_input = simplejson.loads(input_string)
        except simplejson.JSONDecodeError as exc:
            raise TiddlerFormatError(
                    'unable to make json into tiddler: %s, %s'
                    % (tiddler.title, exc))
        accepted_keys = ['created', 'modified', 'modifier', 'tags', 'fields',
                'text', 'type']
        for key, value in dict_from_input.items():
            if value is not None and key in accepted_keys:
                setattr(tiddler, key, value)
        if binary_tiddler(tiddler):
            try:
                tiddler.text = b64decode(tiddler.text)
            except (TypeError, ValueError) as exc:
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
            if tiddler.text:
                if binary_tiddler(tiddler):
                    wanted_info['text'] = b64encode(tiddler.text)
                else:
                    wanted_info['text'] = tiddler.text
            else:
                wanted_info['text'] = ''
        if render and renderable(tiddler, self.environ):
            wanted_info['render'] = render_wikitext(tiddler, self.environ)
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
