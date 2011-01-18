"""
A module containing the Tiddler class and related functions.
"""

import re

from datetime import datetime


def current_timestring():
    """
    Translate (now) into a TiddlyWiki conformat timestring.
    """
    time_object = datetime.utcnow()
    return unicode(time_object.strftime('%Y%m%d%H%M%S'))


def string_to_tags_list(string):
    """
    Given a string representing tags in TiddlyWiki
    format parse them into a list of tag strings.
    """
    tags = []
    tag_matcher = re.compile(r'([^ \]\[]+)|(?:\[\[([^\]]+)\]\])')
    for match in tag_matcher.finditer(string):
        if match.group(2):
            tags.append(match.group(2))
        elif match.group(1):
            tags.append(match.group(1))

    return list(set(tags))


class Tiddler(object):
    """
    The primary content object in the TiddlyWiki universe, vaguely
    corresponding to a Page in other wiki systems. A Tiddler has
    text and some associated metadata. The text can be anything, but
    is usually wikitext in some form, or Javascript code to be used
    as a plugin. It is possible for a Tiddler to container binary
    content, such as image data.

    A Tiddler is intentionally just a container of data. That is, it has
    no methods which change the state of attributes in the Tiddler or
    manipulate the tiddler. Changing the attributes is done by directly
    changing the attributes. This is done to make the Tiddler easier to
    store and serialize in many ways.

    A Tiddler has several attributes:

    title: The name of the tiddler. Required.
    created: A string representing when this tiddler was
            created.
    modified: A string representing when this tiddler was
             last changed. Defaults to now.
    modifier: A string representing a personage that changed
              this tiddler in some way. This doesn't necessarily
              have any assocation with the tiddlyweb.usersign,
              though it may.
    tags: A list of strings that describe the tiddler.
    fields: An arbitrary dictionary of extended fields on the tiddler.
    text: The contents of the tiddler. A string.
    revision: The revision of this tiddler. An int.
    bag: The name of the bag in which this tiddler exists,
         if any. Usually set by internal code.
    recipe: The name of the recipe in which this tiddler exists,
            if any. Usually set by internal code.
    store: A reference to the Store object which retrieved
           this tiddler from persistent storage.
    """

    slots = ['title',
            'created',
            'modified',
            'modifier',
            'creator',
            'tags',
            'fields',
            'text',
            'type',
            'revision',
            'bag',
            'recipe',
            'store']

    def __init__(self, title=None, bag=None):
        """
        Create a new Tiddler object.

        A title is required to ceate a tiddler.
        """
        if title:
            title = unicode(title)
        if bag:
            bag = unicode(bag)
        self.title = title
        self.bag = bag

        self._creator = ''
        self.modifier = None
        self.created = ''
        self.modified = current_timestring()
        self.tags = []
        self.fields = {}
        self.text = ''
        self.type = None
        self.revision = 0
        self.recipe = None
        # reference to the store which 'got' us
        self.store = None

    def _get_creator(self):
        """
        Get the creator of this tiddler. If it has not been
        set then use modifier.

        Use the creator property instead.
        """
        if not self._creator:
            self._creator = self.modifier
        return self._creator

    def _set_creator(self, creator):
        """
        Set the creator of this tiddler.

        Use the creator property instead.
        """
        self._creator = creator

    creator = property(_get_creator, _set_creator)

    def __repr__(self):
        """
        Make the printed tiddler include the title so we
        can distinguish between them while debugging.
        """
        return self.title + object.__repr__(self)
