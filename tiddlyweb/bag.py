"""
A module containing the Bag class and the Policy class
which describes access controls for a Bag.
"""
import copy

from tiddlyweb.auth import ForbiddenError, UserRequiredError


class Policy(object):
    """
    A container for information about the
    contraints on a bag. A bag is something that
    contains tiddlers. We need to be able to say
    who can do what to do those tiddlers. We also
    need to be able to say who can manage those
    constraints.

    The init parameters represent a default policy.
    The default policy should really come from
    server configuration. Then we can declare this
    installation as open-ish, or closed-ish.
    """

    def __init__(self, owner=None,
            read=[], write=[], create=[], delete=[],
            manage=['NONE']):
        self.owner = owner
        self.read = read
        self.write = write
        self.create = create
        self.delete = delete
        self.manage = manage

    def allows(self, user, constraint):
        """
        Is user allowed to perform the action described
        by constraint. The user has a name and some roles,
        either may match in the constraint.
        """
        try:
            roles = user['roles']
        except KeyError:
            roles = []
        user_sign = user['name']

        info_list = self.__getattribute__(constraint)

        # no constraints then all pass
        if len(info_list) == 0:
            return True

        user_list = [x for x in info_list if not x.startswith('R:')]
        role_list = [x[2:] for x in info_list if x.startswith('R:')]

        # always reject if the constraint is NONE
        if len(user_list) == 1 and user_list[0] == 'NONE':
            raise ForbiddenError, '%s may not %s' % (user_sign, constraint)

        # always allow if the constraint is ANY
        if len(user_list) == 1 and user_list[0] == 'ANY':
            if user_sign is not 'GUEST':
                return True

        # if there is an intersection between the users roles and any roles
        # in the constraint, return true
        if [role for role in roles if role in role_list]:
            return True

        # if the user is in the constraint list, return true
        if user_sign in user_list:
            return True

        # if the user is set to GUEST (meaning nobody in credentials)
        # then we don't pass, and we need a user
        if user_sign == 'GUEST':
            raise UserRequiredError, 'real user required to %s' % constraint

        # we've fallen through, the user we have matches nothing
        raise ForbiddenError, '%s may not %s' % (user_sign, constraint)


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

    default_policy = Policy()

    def __init__(self, name, desc='',
            policy=default_policy,
            tmpbag=False, revbag=False, searchbag=False):
        dict.__init__(self)
        self.name = name
        self.desc = desc
        self.policy = policy
        self.tmpbag = tmpbag
        self.revbag = revbag
        self.searchbag = searchbag
        self.order = []
        self.store = None

    def _tiddler_key(self, tiddler):
        """
        Calculate the dict key for indexing this tiddler
        in the bag. If we are a searchbag we need to include bag.
        If we are a revbag we need to include revision. Otherwise
        we just want to use the tiddler.title (so that clobbering
        happens).
        """
        if self.searchbag:
            return '%s.%s.%s' % (tiddler.bag, tiddler.title, tiddler.revision)
        if self.revbag:
            return '%s.%s' % (tiddler.title, tiddler.revision)
        return '%s' % (tiddler.title)

    def _tiddler_copy(self, tiddler):
        """
        If a bag is not a tmpbag, when we put a tiddler in
        it, we need to copy the tiddler, otherwise operations
        that happen to the tiddler in the bag may impact a
        tiddler somewhere else in the process space.
        """
        if self.tmpbag:
            pass
        else:
            bags_tiddler = copy.deepcopy(tiddler)
            bags_tiddler.bag = self.name
            tiddler = bags_tiddler
        return tiddler

    def __getitem__(self, tiddler):
        return dict.__getitem__(self, self._tiddler_key(tiddler))

    def __setitem__(self, tiddler):
        dict.__setitem__(self, self._tiddler_key(tiddler), tiddler)

    def __delitem__(self, tiddler):
        dict.__delitem__(self, self._tiddler_key(tiddler))

    def add_tiddler(self, tiddler):
        """
        Inject a tiddler into the bag. Depending on the
        type of bag in use, this may or may not clobber
        a tiddler of the same name in the bag.
        """
        tiddler = self._tiddler_copy(tiddler)
        if self._tiddler_key(tiddler) in self.order:
            self.order.remove(self._tiddler_key(tiddler))
        self.order.append(self._tiddler_key(tiddler))
        self.__setitem__(tiddler)

    def remove_tiddler(self, tiddler):
        """
        Remove the provided tiddler from the bag.
        """
        if self._tiddler_key(tiddler) in self.order:
            self.order.remove(self._tiddler_key(tiddler))
        self.__delitem__(tiddler)

    def list_tiddlers(self):
        """
        List all the tiddlers in the bag, in the order
        they were added.
        """
        return [self.get(keyword, None) for keyword in self.order]
