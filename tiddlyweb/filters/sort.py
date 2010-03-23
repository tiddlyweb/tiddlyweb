"""
Sort a collection of entities by some attribute.

Part of the filtering system. The syntax is:

    sort=attribute
    sort=-attribute

Atribute is either a real entity attribute or
a key in ATTRIBUTE_SORT_KEY that has as its value
a function used to generate a key to pass to the
sort. ATTRIBUTE_SORT_KEY can be extended by plugins.

If the attribute is prepended with '-' the sort
is reversed.
"""


def date_to_canonical(datestring):
    """
    Take a string of 14 or less digits
    and turn it into 14 digits for the
    sake of comparing entity dates.
    """
    return datestring.ljust(14, '0')


ATTRIBUTE_SORT_KEY = {
        'modified': date_to_canonical,
        'created': date_to_canonical,
        }


def sort_parse(attribute):
    """
    Create a function which will sort a collection of
    entities.
    """
    if attribute.startswith('-'):
        attribute = attribute.replace('-', '', 1)

        def sorter(entities, indexable=False, environ=None):
            return sort_by_attribute(attribute, entities, reverse=True)

    else:

        def sorter(entities, indexable=False, environ=None):
            return sort_by_attribute(attribute, entities)

    return sorter


def sort_by_attribute(attribute, entities, reverse=False):
    """
    Sort a group of entities by some attribute.
    Inspect ATTRIBUTE_SORT_KEY to see if there is a special
    function by which we should generate the value for this
    attribute.
    """

    func = ATTRIBUTE_SORT_KEY.get(attribute, lambda x: x.lower())

    def key_gen(entity):
        try:
            return func(getattr(entity, attribute))
        except AttributeError:
            try:
                return func(entity.fields[attribute])
            except KeyError, exc:
                raise AttributeError('no attribute: %s, %s' % (attribute, exc))

    return (entity for entity in sorted(entities, key=key_gen, reverse=reverse))
