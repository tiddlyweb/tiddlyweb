

def limit_parse(count='0'):
    index = '0'
    if ',' in count:
        index, count = count.split(',', 1)
    index = int(index)
    count = int(count)
    def limiter(tiddlers):
        return limit(tiddlers, index=index, count=count)

    return limiter


def limit(tiddlers, count=0, index=0):
    return tiddlers[index:index+count]

