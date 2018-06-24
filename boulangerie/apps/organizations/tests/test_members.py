#-*- coding:utf-8 -*-
"""
Unit tests for members.
"""
#pylint:disable=redefined-outer-name,wildcard-import,unused-wildcard-import,line-too-long,invalid-name,no-member,unused-import
import json
from rest_framework.test import APIClient
from .fixtures import *

def test_no_authenticated():
    """
    Try to list members while being authenticated:
    must failed.
    """
    client = APIClient()
    response = client.get('/api/0.1/members/')
    assert response.status_code == 403

def test_details_members_no_authenticated():
    """
    Try to details members without being authenticated:
    must failed.
    """
    client = APIClient()
    response = client.get('/api/0.1/members/my_orga/')
    assert response.status_code == 403

def test_list_members_authenticated(user1, user2, login, orga_factory, member_factory):
    """
    Try to list members being authenticated:
    must succeed.
    """
    client = APIClient()
    token1 = login(user1)
    #
    response = client.get('/api/0.1/members/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 200
    assert response.json()['count'] == 1
    assert response.json()['results'][0]['account'] == 'user1'
    assert response.json()['results'][0]['is_owner'] == True
    assert response.json()['results'][0]['is_admin'] == True
    assert response.json()['results'][0]['organization']['name'] == 'user1-default'
    assert response.json()['results'][0]['organization']['description'] == 'default'
    assert response.json()['results'][0]['organization']['stats']['members'] == 1
    assert response.json()['results'][0]['organization']['stats']['invitations'] == 0
    # Create other orga
    orga_factory('my_orga', token1)
    response = client.get('/api/0.1/members/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 200
    assert response.json()['count'] == 2
    assert response.json()['results'][0]['account'] == 'user1'
    assert response.json()['results'][0]['is_owner'] == True
    assert response.json()['results'][0]['is_admin'] == True
    assert response.json()['results'][0]['organization']['name'] == 'my_orga'
    assert response.json()['results'][0]['organization']['description'] == None
    assert response.json()['results'][0]['organization']['stats']['members'] == 1
    assert response.json()['results'][0]['organization']['stats']['invitations'] == 0
    # Invite an other user to the orga
    member_factory('my_orga', user2, token1)
    response = client.get('/api/0.1/members/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 200
    assert response.json()['count'] == 2
    #
    assert response.json()['results'][0]['account'] == 'user1'
    assert response.json()['results'][0]['is_owner'] == True
    assert response.json()['results'][0]['is_admin'] == True
    assert response.json()['results'][0]['organization']['name'] == 'my_orga'
    assert response.json()['results'][0]['organization']['stats']['members'] == 2
    assert response.json()['results'][0]['organization']['stats']['invitations'] == 0

def test_details_members_authenticated(user1, user2, login, orga_factory, member_factory):
    """
    Try to list members being authenticated:
    must succeed.
    """
    client = APIClient()
    token1 = login(user1)
    orga_factory('my_orga', token1)
    response = client.get('/api/0.1/members/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 200
    assert response.json()['count'] == 1
    #
    member_factory('my_orga', user2, token1)
    response = client.get('/api/0.1/members/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 200
    assert response.json()['count'] == 2
    assert 'is_admin' in response.json()['results'][0]
    assert 'is_owner' in response.json()['results'][0]
    assert 'account' in response.json()['results'][0]
    assert 'date_created' in response.json()['results'][0]
    assert 'date_modified' in response.json()['results'][0]

def test_details_no_orga_member(user1, user2, login, orga_factory):
    """
    Given two accounts, they can only details the members of the organizations they belong to.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('orga_user1', token1)
    orga_factory('orga_user2', token2)
    # User1 check
    response = client.get('/api/0.1/members/orga_user1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 200
    response = client.get('/api/0.1/members/orga_user2/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 403
    # User2 Check
    response = client.get('/api/0.1/members/orga_user1/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 403
    response = client.get('/api/0.1/members/orga_user2/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 200

def test_no_head_method(user1, login, orga_factory):
    """
    Try to do a head on a member resource:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    orga_factory('my_orga', token1)
    response = client.head('/api/0.1/members/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 405

def test_no_put_method(user1, login, orga_factory):
    """
    Try to do a PUT on a member resource:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    orga_factory('my_orga', token1)
    response = client.put('/api/0.1/members/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 405

def test_no_post_method(user1, user2, login, orga_factory, member_factory):
    """
    Try to do a POST on a member resource:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    orga_factory('my_orga', token1)
    member_factory('my_orga', user2, token1)
    response = client.post('/api/0.1/members/my_orga/', {'account': 'user2'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 405

def test_patch_member_admin(user1, user2, login, orga_factory, member_factory):
    """
    As an owner, upgrade a member to admin:
    must succeed.
    """
    client = APIClient()
    token1 = login(user1)
    orga_factory('my_orga', token1)
    member_factory('my_orga', user2, token1)
    response = client.patch('/api/0.1/members/my_orga/',{'account':'user2', 'is_admin':True}, HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 204
    # Check
    response = client.get('/api/0.1/members/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    account2 = next(r for r in response.json()['results'] if r['account'] == 'user2')
    assert account2['is_admin'] == True

def test_patch_member_owner(user1, user2, login, orga_factory, member_factory):
    """
    As an owner, upgrade a member to an owner:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    orga_factory('my_orga', token1)
    member_factory('my_orga', user2, token1)
    response = client.patch('/api/0.1/members/my_orga/',{'account':'user2', 'is_owner':True}, HTTP_AUTHORIZATION='JWT {}'.format(token1))
    #Check
    response = client.get('/api/0.1/members/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    account2 = next(r for r in response.json()['results'] if r['account'] == 'user2')
    assert account2['is_owner'] == False

def test_patch_owner(user1, user2, login, orga_factory, member_factory):
    """
    Try to patch the owner of the organization:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    orga_factory('my_orga', token1)
    member_factory('my_orga', user2, token1, is_admin=True)
    response = client.patch('/api/0.1/members/my_orga/',{'account':'user1', 'is_owner':False}, HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 403
    response = client.patch('/api/0.1/members/my_orga/',{'account':'user1', 'is_admin':False}, HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 403

def test_patch_no_admin(user1, user2, user3, login, orga_factory, member_factory):
    """
    As a non admin, upgrade a member to admin:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('my_orga', token1)
    member_factory('my_orga', user2, token1)
    member_factory('my_orga', user3, token1)
    response = client.patch('/api/0.1/members/my_orga/',{'account':'user3', 'is_admin':True}, HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 403

def test_patch_not_member_organization(user1, user2, user3, login, orga_factory, member_factory):
    """
    As a non member, upgrade a member to admin:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('my_orga', token1)
    member_factory('my_orga', user3, token1)
    response = client.patch('/api/0.1/members/my_orga/',{'account':'user3', 'is_admin':True}, HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 404

def test_patch_target_not_member(user1, user2, login, orga_factory, member_factory):
    """
    As an admin, upgrade a non existing member:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    orga_factory('my_orga', token1)
    response = client.patch('/api/0.1/members/my_orga/',{'account':'user2', 'is_admin':True}, HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 404

def test_delete_unauthenticated(user1, user2, login, orga_factory, member_factory):
    """
    Try to delete a member without being authenticated:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    orga_factory('my_orga', token1)
    member_factory('my_orga', user2, token1)
    response = client.delete('/api/0.1/members/my_orga/user2/')
    assert response.status_code == 403

def test_delete_authenticated(user1, user2, login, orga_factory, member_factory):
    """
    Try to delete a member being an authenticated admin:
    must succeed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('my_orga', token1)
    member_factory('my_orga', user2, token1, is_admin=True)
    response = client.delete('/api/0.1/members/my_orga/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 204

def test_delete_two_accounts(user1, user2, user3, login, orga_factory, member_factory):
    """
    Try to delete a member being an authenticated non admin:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    token3 = login(user3)
    orga_factory('my_orga', token1)
    member_factory('my_orga', user2, token1)
    member_factory('my_orga', user3, token1)
    response = client.delete('/api/0.1/members/my_orga/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token3))
    assert response.status_code == 403

def test_delete_as_a_member(user1, user2, login, orga_factory, member_factory):
    """
    Try to delete ourself from the organization, when we are a simple member:
    must succeed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('my_orga', token1)
    member_factory('my_orga', user2, token1)
    response = client.delete('/api/0.1/members/my_orga/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 204

def test_delete_non_member_organization(user1, user2, user3, login, orga_factory, member_factory):
    """
    Try to delete a member from another organization:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('orga1', token1)
    orga_factory('orga2', token2)
    member_factory('orga2', user3, token2)
    ##
    response = client.delete('/api/0.1/members/orga2/user3/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 404

def test_delete_authenticated_admin(user1, user2, user3, login, orga_factory, member_factory):
    """
    Try to delete an admin:
    must succeed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('my_orga', token1)
    member_factory('my_orga', user2, token1, is_admin=True)
    member_factory('my_orga', user3, token1, is_admin=True)
    response = client.delete('/api/0.1/members/my_orga/user3/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 204

def test_delete_authenticated_owner(user1, user2, login, orga_factory, member_factory):
    """
    Try to delete the owner:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('my_orga', token1)
    member_factory('my_orga', user2, token1, is_admin=True)
    response = client.delete('/api/0.1/members/my_orga/user1/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 403

def test_created_send_broker_message(broker_git_create_member, orga_factory, login, member_factory, user1, user2):
    """
    When creating a member, a message must be send to the broker.
    """
    queue, _ = broker_git_create_member
    token1 = login(user1)
    orga_factory('my_orga', token1)
    member_factory('my_orga', user2, token1)
    #
    msg = json.loads(next(queue.consume()).body)
    assert msg == {'organization': 'my_orga', 'account': 'user2'}

def test_member_broker_message(broker_git_delete_member, user1, login, orga_factory, user2, member_factory):
    """
    When deleting a member, a message must be send to the broker.
    """
    queue, _ = broker_git_delete_member
    client = APIClient()
    token1 = login(user1)
    orga_factory('my_orga', token1)
    member_factory('my_orga', user2, token1)
    client.delete('/api/0.1/members/my_orga/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    #
    msg = json.loads(next(queue.consume()).body)
    assert msg == {'organization': 'my_orga', 'account':'user2'}
