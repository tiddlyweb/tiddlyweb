
"""
Test the creation and data handling of policies.
"""

import sys
sys.path.append('.')
from tiddlyweb.bag import Policy, Bag

def setup_module(module):
    pass

def test_policy_create():
    policy = Policy()

    assert type(policy) == Policy
    assert policy.read == []
    assert policy.write == []
    assert policy.create == []
    assert policy.delete == []
    assert policy.manage == ['NONE']

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
    policy = Policy(read=['chris','jeremy'],write=['NONE'],manage=['chris'])

    assert policy.allows('chris', 'read')
    assert policy.allows('jeremy', 'read')
    assert not policy.allows('jeremy', 'write')
    assert policy.allows('chris', 'manage')
    assert not policy.allows('jeremy', 'manage')
    assert policy.allows('chris', 'create')
    assert not policy.allows('NONE', 'write')
    assert not policy.allows('barnabas', 'read')
    assert not policy.allows('barnabas', 'write')
    assert policy.allows('barnabas', 'create')
    assert policy.allows('barnabas', 'delete')
    assert not policy.allows('barnabas', 'manage')

def test_bag_policy():

    bag = Bag('policy_tester')
    bag.policy = Policy(read=['chris','jeremy'])

    assert bag.policy.allows('chris', 'read')
    assert not bag.policy.allows('chris', 'manage')

