"""
A module containing the Bag class.
"""


class ForbiddenError(Exception):
    """
    The provided user cannot do this action.
    """
    pass


class UserRequiredError(Exception):
    """
    To do this action a user is required.
    """
    pass


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
            read=None, write=None, create=None, delete=None,
            manage=None):
        # avoid "dangerous" warnings from pylint and
        # and possible memory leaks
        if read is None:
            read = []
        if write is None:
            write = []
        if create is None:
            create = []
        if delete is None:
            delete = []
        if manage is None:
            manage = []
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
        try:
            if len(info_list) == 0:
                return True
        except TypeError:
            # constraint not set (weirdness in DB)
            return True

        user_list = [x for x in info_list if not x.startswith('R:')]
        role_list = [x[2:] for x in info_list if x.startswith('R:')]

        # always reject if the constraint is NONE
        if len(user_list) == 1 and user_list[0] == 'NONE':
            raise ForbiddenError('%s may not %s' % (user_sign, constraint))

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
            raise UserRequiredError('real user required to %s' % constraint)

        # we've fallen through, the user we have matches nothing
        raise ForbiddenError('%s may not %s' % (user_sign, constraint))

    def user_perms(self, usersign):
        perms = ['read', 'write', 'create', 'delete']
        matched_perms = []
        for perm in perms:
            try:
                self.allows(usersign, perm)
                matched_perms.append(perm)
            except (UserRequiredError, ForbiddenError):
                pass
        return matched_perms


def create_policy_check(environ, entity, usersign):
    """
    Determine if the user in usersign can create entity
    type.
    """
    try:
        entity_policy = '%s_create_policy' % entity
        policy = environ['tiddlyweb.config'][entity_policy]
    except KeyError:
        raise ForbiddenError('create policy not set for %s' % entity)

    if policy == '':
        return True

    if policy == 'ANY':
        if usersign['name'] != 'GUEST':
            return True
        else:
            raise UserRequiredError('authenticated user required to create')

    if policy == 'ADMIN':
        try:
            if 'ADMIN' in usersign['roles']:
                return True
            else:
                raise ForbiddenError('admin role required to create')
        except KeyError:
            raise ForbiddenError('admin role required to create, user has no roles')

    raise ForbiddenError('create access denied')
