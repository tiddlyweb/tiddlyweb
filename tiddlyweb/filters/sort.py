"""
Sort routines.
"""

def sort_by_attribute(attribute, tiddlers, reverse=False):

    def key_gen(x):
        try:
            return getattr(x, attribute).lower()
        except AttributeError:
            try:
                return x.fields[attribute]
            except KeyError, exc:
                raise AttributeError('no attribute: %s, %s' % (attribute, exc))

    return sorted(tiddlers, key=key_gen, reverse=reverse)

