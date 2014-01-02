"""
A module containing the :py:class:`Tiddler` class and related functions.
"""

import re

from datetime import datetime
from time import strptime

from tiddlyweb.fixups import unicode


def current_timestring():
    """
    Translate the current UTC time into a TiddlyWiki conformat timestring.
    """
    time_object = datetime.utcnow()
    return unicode(time_object.strftime('%Y%m%d%H%M%S'))


def timestring_to_datetime(timestring):
    """
    Turn a TiddlyWiki timestring into a datetime object.

    Will raise ValueError if the input is not a 12 or 14
    digit timestring.
    """
    try:
        timestring_datetime = datetime(*(strptime(timestring,
            '%Y%m%d%H%M')[0:6]))
    except ValueError:
        timestring_datetime = datetime(*(strptime(timestring,
            '%Y%m%d%H%M%S')[0:6]))
    return timestring_datetime


def tags_list_to_string(tags):
    """
    Given a list of ``tags``, turn it into the canonical string representation
    (space-delimited, enclosing tags containing spaces in double brackets).
    """
    tag_string_list = []
    for tag in tags:
        if ' ' in tag:
            tag = '[[%s]]' % tag
        tag_string_list.append(tag)
    return u' '.join(tag_string_list)


def string_to_tags_list(string):
    """
    Given a string representing tags (space-delimited, tags containing spaces
    are enclosed in in double brackets), parse them into a list of tag strings.

    Duplicates are removed.
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
    The primary content object in the TiddlyWiki and TiddlyWeb universe,
    representing a distinct piece of content, often vaguely
    corresponding to a Page in wiki systems. A Tiddler has text and some
    associated metadata. The text can be anything, often wikitext in
    some form, or Javascript code. It is possible for a Tiddler to
    container binary content, such as image data.

    A Tiddler is intentionally solely a container of data. That is, it has
    no methods which change the state of attributes in the Tiddler or
    manipulate the tiddler. Changing the attributes is done by directly
    changing the attributes. This is done to make the Tiddler easier to
    :py:class:`store <tiddlyweb.store.Store>` and :py:class:`serialize
    <tiddlyweb.serializer.Serializer>` in many ways.

    A Tiddler has several attributes:

    title
        The name of the tiddler. Required.

    created
        A string representing when this tiddler was created.

    modified
        A string representing when this tiddler was last changed.
        Defaults to now.

    modifier
        A string representing a personage that changed this tiddler in
        some way. This doesn't necessarily have any assocation with the
        tiddlyweb.usersign, though it may.

    tags
        A list of strings that describe the tiddler.

    fields
        An arbitrary dictionary of extended (custom) fields on the tiddler.

    text
        The contents of the tiddler. A string.

    revision
        The revision of this tiddler. The type of a revision is unspecified
        and is :py:class:`store <tiddlyweb.store.Store>` dependent.

    bag
        The name of the bag in which this tiddler exists, if any.

    recipe
        The name of the recipe in which this tiddler exists, if any.

    store
        A reference to the :py:class:`Store <tiddlyweb.store.Store>` object
        which retrieved this tiddler from persistent storage.
    """

    data_members = ['title',
            'creator',
            'created',
            'modifier',
            'modified',
            'tags',
            'fields',
            'type',
            'text']
    # TiddlyWeb-specific attributes
    slots = data_members + ['revision', 'bag', 'recipe', 'store']

    def __init__(self, title=None, bag=None):
        """
        Create a new Tiddler object.

        A ``title`` is required to ceate a tiddler.
        """
        self.title = title
        self.bag = bag

        self._creator = u''
        self.modifier = None
        self.created = u''
        self.modified = current_timestring()
        self.tags = []
        self.fields = {}
        self.text = u''
        self.type = None
        self.revision = None
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
