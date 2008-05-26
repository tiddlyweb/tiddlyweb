import copy

class Bag(dict):
    """
    XXX: We should subclass for tmpbag and revbag.

    A Bag is a collection of tiddlers, usually unique by
    the title of the tiddler. A bag can have tiddlers added, removed,
    and listed.

    A Bag which has been retrieved from a Store will have
    its 'store' attribute set to the store it was retrieved
    from. This makes it possible to later lazily load the
    tiddlers that are in the bag.

    At some point the bag will have a security policy and
    add and remove will throw permissions exceptions. TBD.
    """

    default_policy = "all the world's a stage"

    def __init__(self, name, policy=default_policy, tmpbag=False, revbag=False):
        dict.__init__(self)
        self.name = name
        self.policy = policy
        self.tmpbag = tmpbag
        self.revbag = revbag
        self.order = []
        self.store = None

    def _tiddler_key(self, tiddler):
        return '%s.%s' % (tiddler.title, tiddler.revision)

    def _tiddler_copy(self, tiddler):
        if self.tmpbag:
            pass
        else:
            bags_tiddler = copy.deepcopy(tiddler)
            bags_tiddler.bag = self.name
            tiddler = bags_tiddler
        return tiddler

    def __getitem__(self, tiddler):
        return dict.__getitem__(self, self._tiddler_key(tiddler) )

    def __setitem__(self, tiddler):
        dict.__setitem__(self, self._tiddler_key(tiddler), tiddler)

    def __delitem__(self, tiddler):
        dict.__delitem__(self, self._tiddler_key(tiddler))

    def add_tiddler(self, tiddler):
        tiddler = self._tiddler_copy(tiddler)
        if self._tiddler_key(tiddler) in self.order:
            self.order.remove(self._tiddler_key(tiddler))
        self.order.append(self._tiddler_key(tiddler))
        self.__setitem__(tiddler)

    def remove_tiddler(self, tiddler):
        if self._tiddler_key(tiddler) in self.order:
            self.order.remove(self._tiddler_key(tiddler))
        self.__delitem__(tiddler)

    def list_tiddlers(self):
        return [self.get(keyword, None) for keyword in self.order]

class Policy(object):
    """
    A container for information about the 
    contraints on a bag. A bag is something that
    contains tiddlers. We need to be able to say
    who can do what to do those tiddlers. We also
    need to be able to say who can manage those
    constraints.
    """

    def __init__(self, owner=None, read=[], write=[], create=[], delete=[], manage=['NONE']):
        self.owner = owner
        self.read = read
        self.write = write
        self.create = create
        self.delete = delete
        self.manage = manage

    def allows(self, user_sign, constraint):
        user_list = self.__getattribute__(constraint)
        if len(user_list) == 0:
            return True
        if len(user_list) == 1 and user_list[0] == 'NONE':
            return False
        return user_sign in self.__getattribute__(constraint)
