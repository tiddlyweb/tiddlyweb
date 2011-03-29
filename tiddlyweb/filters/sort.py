"""
Sort a collection of entities by some attribute. The syntax is:

    sort=attribute   # sort ascending
    sort=-attribute  # sort descending

Atribute is either a real entity attribute or a key in
ATTRIBUTE_SORT_KEY that has as its value a function used to generate a
key to pass to the sort. ATTRIBUTE_SORT_KEY can be extended by plugins.
"""

from tiddlyweb.model.tiddler import Tiddler


def date_to_canonical(datestring):
    """
    Take a string of 14 or less digits
    and turn it into 14 digits for the
    sake of comparing entity dates.
    """
    return datestring.ljust(14, '0')


def as_int(attribute):
    """
    Treat attribute as int if it looks like one.
    """
    try:
        return int(attribute)
    except ValueError:
        return attribute


ATTRIBUTE_SORT_KEY = {
        'modified': date_to_canonical,
        'created': date_to_canonical,
        'revision': as_int,
        }


def sort_parse(attribute):
    """
    Create a function which will sort a collection of
    entities.
    """
    if attribute.startswith('-'):
        attribute = attribute.replace('-', '', 1)

        def sorter(entities, indexable=False, environ=None):
            return sort_by_attribute(attribute, entities, reverse=True,
                    environ=environ)

    else:

        def sorter(entities, indexable=False, environ=None):
            return sort_by_attribute(attribute, entities, environ=environ)

    return sorter


def sort_by_attribute(attribute, entities, reverse=False, environ=None):
    """
    Sort a group of entities by some attribute.
    Inspect ATTRIBUTE_SORT_KEY to see if there is a special
    function by which we should generate the value for this
    attribute.
    """
    if environ == None:
        environ = {}

    store = environ.get('tiddlyweb.store', None)

    func = ATTRIBUTE_SORT_KEY.get(attribute, lambda x: x.lower())

    def key_gen(entity):
        """
        Reify the attribute needed for sorting. If the entity
        has not already been loaded from the store, do so.
        """
        if store and not entity.store:
            stored_entity = Tiddler(entity.title, entity.bag)
            if entity.revision:
                stored_entity.revision = entity.revision
            stored_entity = store.get(stored_entity)
        else:
            stored_entity = entity
        try:
            return func(getattr(stored_entity, attribute))
        except AttributeError, attribute_exc:
            try:
                return func(stored_entity.fields[attribute])
            except (AttributeError, KeyError), exc:
                raise AttributeError('on %s, no attribute: %s, %s, %s'
                        % (stored_entity, attribute, attribute_exc, exc))

    return (entity for entity in
            sorted(entities, key=key_gen, reverse=reverse))
