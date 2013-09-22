"""
A module containing the :py:class:`Policy` class and associated
exceptions.
"""


class PermissionsError(Exception):
    """
    Base class for :py:class:`Policy` violations.
    """


class ForbiddenError(PermissionsError):
    """
    The provided user cannot do this action.
    """
    pass


class UserRequiredError(PermissionsError):
    """
    To do this action a user is required.
    """
    pass


class Policy(object):
    """
    A container for information about the contraints on a :py:class:`bag
    <tiddlyweb.model.bag.Bag>` or :py:class:`recipe
    <tiddlyweb.model.recipe.Recipe>`. Both are containers of
    :py:class:`tiddlers <tiddlyweb.model.tiddler.Tiddler>`. We need to
    be able to control who can do what to do those tiddlers. We also
    need to be able to control who can manage those constraints.

    The :pu:func:__init__ parameters represent a default policy.

    There are six constraints plus one identifying attribute (``owner``).
    The constraints are listed below with descriptions of what is allowed
    if the constraint passes.

    read
        View this entity in lists. View the contained entities.

    write
        Edit the contained entities that already exist.

    create
        Create new entities in the container.

    delete
        Remove a contained entity.

    manage
        Change the policy itself.

    accept
         Accept the entity into the container without requiring
         :py:mod:`validation <tiddlyweb.web.validator>`.
    """

    attributes = [u'read', u'write', u'create', u'delete', u'manage',
            u'accept', u'owner']

    def __init__(self, owner=None,
            read=None, write=None, create=None, delete=None,
            manage=None, accept=None):
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
        if accept is None:
            accept = []
        self.owner = owner
        self.read = read
        self.write = write
        self.create = create
        self.delete = delete
        self.manage = manage
        self.accept = accept

    def allows(self, usersign, constraint):
        """
        Is the user encapsulated by the ``usersign`` dict allowed to
        perform the action described by ``constraint``. If so, return
        True. If not raise a :py:class:`UserRequiredError` (if the user is
        ``GUEST``) or :py:class:`ForbiddenError` exception.

        The dict has a ``name`` key with a string value which is a
        ``username`` and a ``roles`` key with a list of roles as its value.
        Either may match in the constraint. Usersign is usually populated
        during the :py:class:`CredentialsExtractor
        <tiddlyweb.web.extractors.ExtractorInterface>` phase of a
        request.
        """
        try:
            roles = usersign['roles']
        except KeyError:
            roles = []
        username = usersign['name']

        info_list = self.__getattribute__(constraint)

        if _no_constraint(info_list):
            return True

        user_list = [x for x in info_list if not x.startswith('R:')]

        # always reject if the constraint is NONE
        if _single_value_set(user_list, u'NONE'):
            raise ForbiddenError('%s may not %s' % (username, constraint))

        if _user_valid(username, user_list):
            return True

        role_list = [x[2:] for x in info_list if x.startswith('R:')]

        if _role_valid(roles, role_list):
            return True

        # if the user is set to GUEST (meaning nobody in credentials)
        # then we don't pass, and we need a user
        if username == u'GUEST':
            raise UserRequiredError('real user required to %s' % constraint)

        # we've fallen through, the user we have matches nothing
        raise ForbiddenError('%s may not %s' % (username, constraint))

    def user_perms(self, usersign):
        """
        For this policy return a list of constraints for which
        this usersign passes.
        """
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
    Determine if the user in ``usersign`` can create ``entity`` type.
    """
    try:
        entity_policy = '%s_create_policy' % entity
        policy = environ['tiddlyweb.config'][entity_policy]
    except KeyError:
        raise ForbiddenError('create policy not set for %s' % entity)

    if policy == '':
        return True

    if policy == u'ANY':
        if usersign['name'] != u'GUEST':
            return True
        else:
            raise UserRequiredError('authenticated user required to create')

    if policy == u'ADMIN':
        try:
            if u'ADMIN' in usersign['roles']:
                return True
            else:
                raise ForbiddenError('admin role required to create')
        except KeyError:
            raise ForbiddenError(
                    'admin role required to create, user has no roles')

    raise ForbiddenError('create access denied')


def _single_value_set(target_list, value):
    """
    Return true if this constraint has only one value and it is
    this one.
    """
    return len(target_list) == 1 and target_list[0] == value


def _no_constraint(info_list):
    """
    If there is no constraint set, then anything passes.
    """
    try:
        if len(info_list) == 0:
            return True
    except TypeError:
        # constraint not set (weirdness in DB)
        return True

    return False


def _role_valid(roles, role_list):
    """
    Return ``True`` if there is an intersection between the users roles
    and any roles in the constraint.
    """
    if [role for role in roles if role in role_list]:
        return True
    return False


def _user_valid(user_sign, user_list):
    """
    If the user_sign is in the constraint or the constraint value
    is ANY, return true.
    """
    if _single_value_set(user_list, u'ANY'):
        if user_sign != u'GUEST':
            return True

    if user_sign in user_list:
        return True

    return False
