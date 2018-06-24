#-*- coding:utf-8 -*-
"""
Unit tests for organizations.
"""
#pylint:disable=redefined-outer-name,wildcard-import,unused-wildcard-import,line-too-long,invalid-name,no-member,unused-import
import json
from rest_framework.test import APIClient
from .fixtures import *

def test_creation_no_authenticated():
    """
    Try to create an organization without being authenticated:
    must failed.
    """
    client = APIClient()
    response = client.post('/api/0.1/organizations/', {'name': 'my_orga'}, format='json')
    assert response.status_code == 403

def test_creation_authenticated(user1, login):
    """
    Try to create an organization being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/organizations/', {'name': 'my_orga'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201

def test_creation_owner_created(user1, login):
    """
    When an organization is created, a member is created with the flag owner.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/organizations/', {'name': 'my_orga'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201

def test_creation_same_name_error(user1, login):
    """
    Try to create two organizations with the same name:
    must failed the second time.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/organizations/', {'name': 'my_orga'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    ##
    response = client.post('/api/0.1/organizations/', {'name': 'my_orga'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 400

def test_creation_same_name_uppercase_error(user1, login):
    """
    Try to create two organizations with the same name but with different case:
    must failed the second time.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/organizations/', {'name': 'my_orga'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    ##
    response = client.post('/api/0.1/organizations/', {'name': 'My_Orga'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 400

def test_creation_same_name_username(user1, login):
    """
    Try to create an organization with the same name as an account:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/organizations/', {'name': user1}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 400

def test_list_organizations_no_authentication():
    """
    Try to list organizations without being authenticated:
    must failed.
    """
    client = APIClient()
    response = client.get('/api/0.1/organizations/')
    assert response.status_code == 403

def test_list_organizations_authenticated(user1, login, orga_factory):
    """
    Try to list organizations being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.get('/api/0.1/organizations/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 200
    assert response.json()['count'] == 1
    assert response.json()['results'][0]['name'] == 'user1-default'
    assert response.json()['results'][0]['description'] == 'default'
    assert response.json()['results'][0]['stats']['members'] == 1
    assert response.json()['results'][0]['stats']['invitations'] == 0
    assert response.json()['results'][0]['date_created']
    assert response.json()['results'][0]['date_modified']
    #
    orga_factory('My_orga', token, 'MyOrga')
    response = client.get('/api/0.1/organizations/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['count'] == 2
    assert response.json()['results'][0]['name'] == 'my_orga'
    assert response.json()['results'][0]['description'] == 'myorga'
    assert response.json()['results'][0]['date_created']
    assert response.json()['results'][0]['date_modified']

def test_list_organizations_two_accounts(user1, user2, login, orga_factory):
    """
    Given two accounts, list theirs organizations : must only see their own.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('orga_user1', token1)
    orga_factory('orga_again_user1', token1)
    orga_factory('orga_user2', token2)
    # User1 check
    response = client.get('/api/0.1/organizations/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.json()['count'] == 3
    assert 'orga_user1' in [i['name'] for i in response.json()['results']]
    assert 'orga_again_user1' in [i['name'] for i in response.json()['results']]
    assert 'orga_user2' not in [i['name'] for i in response.json()['results']]
    # User2 Check
    response = client.get('/api/0.1/organizations/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.json()['count'] == 2
    assert 'orga_user1' not in [i['name'] for i in response.json()['results']]
    assert 'orga_again_user1' not in [i['name'] for i in response.json()['results']]
    assert 'orga_user2' in [i['name'] for i in response.json()['results']]

def test_detail_organization_unauthenticated(user1, login, orga_factory):
    """
    Try to access to a detail of an organization without being authenticated:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    orga_factory('my_orga', token)
    response = client.get('/api/0.1/organizations/my_orga/')
    assert response.status_code == 403

def test_detail_organization_authenticated(user1, login, orga_factory):
    """
    Try to access to a detail of an organization being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    orga_factory('my_orga', token)
    response = client.get('/api/0.1/organizations/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 200
    assert response.json()['name'] == 'my_orga'
    assert response.json()['description'] == None
    assert response.json()['date_created']
    assert response.json()['date_modified']
    # Non existing
    response = client.get('/api/0.1/organizations/my_wrong_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 404

def test_detail_organization_two_accounts(user1, user2, login, orga_factory):
    """
    Accounts must only access of the details to their orgas.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('orga1', token1)
    orga_factory('orga2', token2)
    ##
    response = client.get('/api/0.1/organizations/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 200
    response = client.get('/api/0.1/organizations/orga2/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 404
    ##
    response = client.get('/api/0.1/organizations/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 404
    response = client.get('/api/0.1/organizations/orga2/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 200

def test_no_head_method(user1, login, orga_factory):
    """
    Try to do a head on an organization resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    orga_factory('my_orga', token)
    response = client.head('/api/0.1/organizations/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 405

def test_no_put_method(user1, login, orga_factory):
    """
    Try to do a PUT on an organization resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    orga_factory('my_orga', token)
    response = client.patch('/api/0.1/organizations/my_orga/', {'name': 'myorga'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 405

def test_no_patch_method(user1, login, orga_factory):
    """
    Try to do a PATCH on a organization resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    orga_factory('my_orga', token)
    response = client.patch('/api/0.1/organizations/my_orga/', {'name': 'myorga'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 405

def test_delete_unauthenticated(user1, login, orga_factory):
    """
    Try to delete an organization without being authenticated:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    orga_factory('my_orga', token)
    response = client.delete('/api/0.1/organizations/my_orga/')
    assert response.status_code == 403
    ##
    response = client.delete('/api/0.1/organizations/my_wrong_orga/')
    assert response.status_code == 403

def test_delete_non_deletable(user1, login, orga_factory):
    """
    Try to delete an organization non deletable:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    response = client.get('/api/0.1/organizations/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['count'] == 1
    ##
    response = client.delete('/api/0.1/organizations/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 403

def test_delete_created_non_deletable(user1, login, orga_factory):
    """
    Try to delete an newly created organization non deletable:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    orga_factory('my_orga', token, deletable=False)
    ##
    response = client.delete('/api/0.1/organizations/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 403

def test_delete_authenticated(user1, login, orga_factory):
    """
    Try to delete an organiation being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    orga_factory('my_orga', token)
    response = client.get('/api/0.1/organizations/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['count'] == 2
    ##
    response = client.delete('/api/0.1/organizations/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 204
    ##
    response = client.get('/api/0.1/organizations/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['count'] == 1
    ##
    response = client.delete('/api/0.1/organizations/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 404

def test_delete_two_accounts(user1, user2, login, orga_factory):
    """
    Accounts can only be able to delete their organizations.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    orga_factory('orga1', token1)
    orga_factory('orga2', token2)
    ##
    response = client.delete('/api/0.1/organizations/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 404
    response = client.delete('/api/0.1/organizations/orga2/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 404
    ##
    response = client.delete('/api/0.1/organizations/orga1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 204
    response = client.delete('/api/0.1/organizations/orga2/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 204

def test_delete_non_owner(user1, user2, user3, login, orga_factory, member_factory):
    """
    Only owner can delete the organization.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    token3 = login(user3)
    orga_factory('my_orga', token1)
    member_factory('my_orga', user2, token1)
    member_factory('my_orga', user3, token1, is_admin=True)
    #1. Simple member
    response = client.delete('/api/0.1/organizations/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 403
    #2. Even admin
    response = client.delete('/api/0.1/organizations/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token3))
    assert response.status_code == 403

def test_created_send_broker_message(broker_git_create_member, orga_factory, login, user1):
    """
    When creating an organization, a member creation message must be send to the broker.
    """
    queue, _ = broker_git_create_member
    token1 = login(user1)
    orga_factory('my_orga', token1)
    #
    msg = json.loads(next(queue.consume()).body)
    assert msg == {'organization': 'my_orga', 'account': 'user1'}

def test_deleted_send_broker_message(broker_git_delete_orga, user1, login, orga_factory):
    """
    When deleting an organization, a message must be send to the broker.
    """
    queue, _ = broker_git_delete_orga
    client = APIClient()
    token1 = login(user1)
    orga_factory('my_orga', token1)
    client.delete('/api/0.1/organizations/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    #
    msg = json.loads(next(queue.consume()).body)
    assert msg == {'organization': 'my_orga'}
