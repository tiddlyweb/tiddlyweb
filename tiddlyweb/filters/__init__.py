
def recursive_filter(filters, tiddlers):
    if len(filters) == 0:
        return tiddlers
    filter = filters.pop(0)
    return recursive_filter(filters, filter(tiddlers))
