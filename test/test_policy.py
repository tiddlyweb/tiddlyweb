
"""
Test the creation and data handling of policies.
"""

import sys
sys.path.append('.')
from tiddlyweb.bag import Policy, Bag

import py.test
from tiddlyweb.auth import ForbiddenError, UserRequiredError

jeremy_info = {'name':'jeremy'}
chris_info = {'name':'chris','roles':['R:ADMIN']}
none_info = {'name':'NONE'}
barnabas_info = {'name':'barnabas'}
randomer_info = {'name':'randomer'}
boom_info = {'name':'boom'}
guest_info = {'name':'GUEST'}

def setup_module(module):
    pass

def test_policy_create():
    policy = Policy()

    assert type(policy) == Policy
    assert policy.read == []
    assert policy.write == []
    assert policy.create == []
    assert policy.delete == []
    assert policy.manage == []

def test_policy_init_set():
    policy = Policy(read=['chris','jeremy'],write=['NONE'],manage=['chris'])

    assert policy.read == ['chris','jeremy']
    assert policy.write == ['NONE']
    assert policy.create == []
    assert policy.delete == []
    assert policy.manage == ['chris']

def test_policy_post_set():
    policy = Policy(read=['chris','jeremy'],write=['NONE'],manage=['chris'])

    assert policy.read == ['chris','jeremy']

    policy.read = ['one','tall']

    assert 'chris' not in policy.read
    assert 'jeremy' not in policy.read
    assert 'tall' in policy.read

def test_policy_allows():
    policy = Policy(read=['chris','jeremy'],write=['NONE'],delete=['R:ADMIN'],manage=['chris'])

    assert policy.allows(chris_info, 'read')
    assert policy.allows(jeremy_info, 'read')
    py.test.raises(ForbiddenError, 'policy.allows(jeremy_info, "write")')
    assert policy.allows(chris_info, 'manage')
    py.test.raises(ForbiddenError, 'policy.allows(jeremy_info, "manage")')
    assert policy.allows(chris_info, 'create')
    py.test.raises(ForbiddenError, 'policy.allows(none_info, "write")')
    py.test.raises(ForbiddenError, 'policy.allows(barnabas_info, "read")')
    py.test.raises(ForbiddenError, 'policy.allows(barnabas_info, "write")')
    assert policy.allows(barnabas_info, 'create')
    py.test.raises(ForbiddenError, 'policy.allows(barnabas_info, "manage")')

def test_policy_any():
    policy = Policy(read=['ANY'],write=['ANY'])
    assert policy.allows(randomer_info, 'read')
    assert policy.allows(boom_info, 'write')
    py.test.raises(UserRequiredError, 'policy.allows(guest_info, "read")')

def test_bag_policy():

    bag = Bag('policy_tester')
    bag.policy = Policy(read=['chris','jeremy'])

    assert bag.policy.allows(chris_info, 'read')
    py.test.raises(UserRequiredError, 'bag.policy.allows(guest_info, "read")')

