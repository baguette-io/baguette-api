#-*- coding:utf-8 -*-
"""
Unit tests for invitations.
"""
#pylint:disable=redefined-outer-name,wildcard-import,unused-wildcard-import,line-too-long,invalid-name,no-member,unused-import
import json
from rest_framework.test import APIClient
from .fixtures import *

def test_creation_no_authenticated():
    """
    Try to create an invitation without being authenticated:
    must failed.
    """
    client = APIClient()
    response = client.post('/api/0.1/invitations/', {'organization': 'my_orga'}, format='json')
    assert response.status_code == 403

def test_creation_authenticated_no_orga(user1, user2, login):
    """
    Try to create an invitation with a organization that does not exist while being authenticated:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    response = client.post('/api/0.1/invitations/', {'organization': 'my_orga', 'account':'user2'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 400

def test_creation_authenticated_no_orga_exist(user1, user2, login, orga_factory):
    """
    Try to create an invitation with an organization that exists but don't belong to ; while being authenticated:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('my_orga', token2)
    response = client.post('/api/0.1/invitations/', {'organization': 'my_orga', 'account':'user2'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 404

def test_creation_authenticated_with_orga(user1, user2, login, orga_factory):
    """
    Try to create an invitation with an organization while being authenticated:
    must succeed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('orga1', token1)
    response = client.post('/api/0.1/invitations/', {'organization': 'orga1', 'account':'user2'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 201
    assert response.json()['organization']['name'] == 'orga1'
    assert response.json()['organization']['stats']['members'] == 1
    assert response.json()['organization']['stats']['invitations'] == 1

def test_creation_authenticated_list_orga(user1, user2, login, orga_factory):
    """
    After creating an invitation with an organization while being authenticated, list the organization. Invit should be displayed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('orga1', token1)
    response = client.post('/api/0.1/invitations/', {'organization': 'orga1', 'account':'user2'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 201
    #
    response = client.get('/api/0.1/invitations/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.json()['count'] == 1
    assert response.json()['results'][0]['account'] == 'user2'
    assert response.json()['results'][0]['organization']['name'] == 'orga1'
    assert response.json()['results'][0]['organization']['stats']['members'] == 1
    assert response.json()['results'][0]['organization']['stats']['invitations'] == 1
    assert response.json()['results'][0]['date_created']

def test_creation_authenticated_already_orga(user1, user2, login, orga_factory):
    """
    Try to create an invitation with an organization already member while being authenticated:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    orga_factory('orga1', token1)
    response = client.post('/api/0.1/invitations/', {'organization': 'orga1', 'account':'user1'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 409

def test_creation_authenticated_already_orga(user1, user2, login, orga_factory):
    """
    Try to create an invitation with an organization where a pending invitation is already existing:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    orga_factory('orga1', token1)
    response = client.post('/api/0.1/invitations/', {'organization': 'orga1', 'account':'user2'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 201
    #
    response = client.post('/api/0.1/invitations/', {'organization': 'orga1', 'account':'user2'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 400

def test_creation_list_orga(user1, user2, login, orga_factory):
    """
    When creating an invitation, and listing an organization, the invitation should be displayed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('orga1', token1)
    #
    response = client.get('/api/0.1/invitations/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.json()['count'] == 0
    #
    response = client.post('/api/0.1/invitations/', {'organization': 'orga1', 'account':'user2'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    #
    response = client.get('/api/0.1/invitations/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.json()['count'] == 1

def test_list_invitations_no_authentication():
    """
    Try to list invitations without being authenticated:
    must failed.
    """
    client = APIClient()
    response = client.get('/api/0.1/invitations/')
    assert response.status_code == 403

def test_list_invitations_authenticated(user1, user2, login, orga_factory, invit_factory):
    """
    Try to list invitations being authenticated:
    must succeed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('my_orga', token1)
    response = client.get('/api/0.1/invitations/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 200
    assert response.json()['count'] == 0
    #
    invit_factory('my_orga', 'user2', token1)
    response = client.get('/api/0.1/invitations/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.json()['count'] == 1
    assert response.json()['results'][0]['organization']['name'] == 'my_orga'
    assert response.json()['results'][0]['account'] == 'user2'
    assert response.json()['results'][0]['date_created']

def test_list_invitations_three_accounts(user1, user2, user3, login, orga_factory, invit_factory):
    """
    Given three accounts, list theirs invitations : must only see their own.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    token3 = login(user3)
    orga_factory('orga_user1', token1)
    orga_factory('orga_user2', token2)
    ## User1 invits User2
    invit_factory('orga_user1', 'user2', token1)
    # User1 check
    response = client.get('/api/0.1/invitations/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.json()['count'] == 0
    # User2 Check
    response = client.get('/api/0.1/invitations/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.json()['count'] == 1
    # User3 Check
    response = client.get('/api/0.1/invitations/', HTTP_AUTHORIZATION='JWT {}'.format(token3))
    assert response.json()['count'] == 0
    ## User2 invits User3
    invit_factory('orga_user2', 'user3', token2)
    # User1 check
    response = client.get('/api/0.1/invitations/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.json()['count'] == 0
    # User2 Check
    response = client.get('/api/0.1/invitations/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.json()['count'] == 1
    # User3 Check
    response = client.get('/api/0.1/invitations/', HTTP_AUTHORIZATION='JWT {}'.format(token3))
    assert response.json()['count'] == 1

def test_detail_invitation_unauthenticated(user1, user2, login, orga_factory, invit_factory):
    """
    Try to access to a detail of an invitation without being authenticated:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    orga_factory('my_orga', token1)
    invit_factory('my_orga', 'user2', token1)
    response = client.get('/api/0.1/invitations/my_orga/')
    assert response.status_code == 403

def test_detail_invitation_authenticated(user1, user2, login, orga_factory, invit_factory):
    """
    Try to access to an organization invitations while being a member of it:
    must success.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('my_orga', token1)
    invit_factory('my_orga', 'user2', token1)
    response = client.get('/api/0.1/invitations/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 200
    assert response.json()['count'] == 1
    response = client.get('/api/0.1/invitations/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 404
    response = client.get('/api/0.1/invitations/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 200
    assert response.json()['count'] == 1

def test_no_head_method(user1, user2, login, orga_factory, invit_factory):
    """
    Try to do a head on an invitation resource:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('my_orga', token1)
    invit_factory('my_orga', 'user2', token1)
    response = client.head('/api/0.1/invitations/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 405

def test_no_patch_method(user1, user2, login, orga_factory, invit_factory):
    """
    Try to do a PATCH on an invitation resource:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('my_orga', token1)
    invit_factory('my_orga', 'user2', token1)
    response = client.patch('/api/0.1/invitations/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 405

def test_delete_unauthenticated(user1, user2, login, orga_factory, invit_factory):
    """
    Try to delete an invitation without being authenticated:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('my_orga', token1)
    invit_factory('my_orga', 'user2', token1)
    response = client.delete('/api/0.1/invitations/my_orga/user2/')
    assert response.status_code == 403

def test_delete_authenticated(user1, user2, login, orga_factory, invit_factory):
    """
    Try to delete an organization being authenticated:
    must succeed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('my_orga', token1)
    invit_factory('my_orga', 'user2', token1)
    response = client.get('/api/0.1/invitations/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.json()['count'] == 1
    ##
    response = client.delete('/api/0.1/invitations/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 404
    ##
    response = client.delete('/api/0.1/invitations/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 404
    ##
    response = client.delete('/api/0.1/invitations/my_orga/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 204
    ##
    response = client.get('/api/0.1/invitations/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.json()['count'] == 0
    ##
    response = client.delete('/api/0.1/invitations/my_orga/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 404

def test_delete_two_accounts(user1, user2, user3, login, orga_factory, invit_factory):
    """
    Accounts can only be able to delete their invitations.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    token3 = login(user3)
    orga_factory('orga1', token1)
    orga_factory('orga2', token2)
    invit_factory('orga1', 'user2', token1)
    invit_factory('orga2', 'user1', token2)
    ##
    response = client.delete('/api/0.1/invitations/orga1/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token3))
    assert response.status_code == 404
    response = client.delete('/api/0.1/invitations/orga2/user1/', HTTP_AUTHORIZATION='JWT {}'.format(token3))
    assert response.status_code == 404
    ##
    response = client.delete('/api/0.1/invitations/orga1/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 204
    response = client.delete('/api/0.1/invitations/orga2/user1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 204

def test_delete_invitation_organization(user1, user2, login, orga_factory, invit_factory):
    """
    An admin from an organization can delete an invitation.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('orga1', token1)
    invit_factory('orga1', 'user2', token1)
    ##
    response = client.delete('/api/0.1/invitations/orga1/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 204
    response = client.delete('/api/0.1/invitations/orga1/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 404

def test_accept_invit_no_authenticated(user1, user2, login, orga_factory, invit_factory):
    """
    Try to do a PUT on an invitation resource without being authenticated:
    must failed.
    """
    client = APIClient()
    token1 = login(user1)
    orga_factory('orga1', token1)
    invit_factory('orga1', 'user2', token1)
    response = client.put('/api/0.1/invitations/orga1/')
    assert response.status_code == 403

def test_accept_invit_authenticated(user1, user2, login, orga_factory, invit_factory):
    """
    Try to do a PUT on an invitation resource being authenticated:
    must succeed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('orga1', token1)
    invit_factory('orga1', 'user2', token1)
    #
    response = client.get('/api/0.1/invitations/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 200
    assert response.json()['count'] == 1
    response = client.get('/api/0.1/members/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.json()['count'] == 1
    #
    response = client.put('/api/0.1/invitations/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 204
    #
    response = client.get('/api/0.1/invitations/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 200
    assert response.json()['count'] == 0
    response = client.get('/api/0.1/members/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.json()['count'] == 2
    #
    response = client.put('/api/0.1/invitations/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 404

def test_accept_invit_two_accounts(user1, user2, user3, login, orga_factory, invit_factory):
    """
    Users can only accepts theirs invitations.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    token3 = login(user3)
    orga_factory('orga1', token1)
    orga_factory('orga2', token2)
    invit_factory('orga1', 'user2', token1)
    invit_factory('orga2', 'user1', token2)
    #
    response = client.put('/api/0.1/invitations/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 404
    response = client.put('/api/0.1/invitations/orga2/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 404
    response = client.put('/api/0.1/invitations/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token3))
    assert response.status_code == 404
    response = client.put('/api/0.1/invitations/orga2/', HTTP_AUTHORIZATION='JWT {}'.format(token3))
    assert response.status_code == 404
    #
    response = client.put('/api/0.1/invitations/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 204
    response = client.put('/api/0.1/invitations/orga2/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 204
