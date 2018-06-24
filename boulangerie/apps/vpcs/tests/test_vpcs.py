#-*- coding:utf-8 -*-
"""
Unit tests for VPCs.
"""
#pylint:disable=redefined-outer-name,wildcard-import,unused-wildcard-import,line-too-long,invalid-name,no-member,unused-import
import json
from rest_framework.test import APIClient
from .fixtures import *

def test_creation_no_authenticated(user1):
    """
    Try to create a VPC without being authenticated:
    must failed.
    """
    client = APIClient()
    response = client.post('/api/0.1/vpcs/user1-default/', {'name': 'my_vpc'}, format='json')
    assert response.status_code == 403

def test_default_vpc(user1, login):
    """
    Test that by default every account has a `default` vpc.
    """
    client = APIClient()
    token = login(user1)
    response = client.get('/api/0.1/vpcs/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['count'] == 1
    response = client.get('/api/0.1/vpcs/user1-default/default/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['name'] == 'default'
    assert response.json()['deletable'] is False
    assert response.json()['date_created']
    assert response.json()['date_modified']

def test_wrong_organization_not_exist(user1, login):
    """
    Test that we cannot access an organization that does not exist.
    """
    client = APIClient()
    token = login(user1)
    response = client.get('/api/0.1/vpcs/toto/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 403

def test_wrong_organization_not_member(user1, user2, login):
    """
    Test that we cannot access an organization that we don't belong to.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    response = client.get('/api/0.1/vpcs/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 200
    response = client.get('/api/0.1/vpcs/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 403

def test_creation_authenticated(user1, login):
    """
    Try to create a VPC being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/vpcs/user1-default/', {'name': 'my_vpc'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201

def test_creation_authenticated_not_member(user1, user2, login):
    """
    Try to create a VPC being authenticated in an organization we don't belong:
    must failed.
    """
    client = APIClient()
    token = login(user2)
    response = client.post('/api/0.1/vpcs/user1-default/', {'name': 'my_vpc'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 403

def test_creation_authenticated_deletable_ignored(user1, login):
    """
    Try to create a VPC being authenticated and with deletable as parameter:
    must succeed and deletable is ignored.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/vpcs/user1-default/', {'name': 'my_vpc', 'deletable': False}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    assert response.json()['deletable'] is True

def test_creation_same_name_error(user1, login):
    """
    Try to create two VPCS with the same user and the same name:
    must failed the second time.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/vpcs/user1-default/', {'name': 'my_vpc'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    ##
    response = client.post('/api/0.1/vpcs/user1-default/', {'name': 'my_vpc'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 400

def test_creation_same_name_two_users(user1, user2, login):
    """
    Try to create two VPCS with the same name using two different users:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/vpcs/user1-default/', {'name': 'my_vpc'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    ##
    token = login(user2)
    response = client.post('/api/0.1/vpcs/user2-default/', {'name': 'my_vpc'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201

def test_create_vpc_not_admin(user1, user2, login, member_factory, vpc_factory):
    """
    Try to create a VPC as a non admin: must failed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    member_factory('user1-default', user2, token1)
    response = client.post('/api/0.1/vpcs/user1-default/', {'name':'tocreate'}, HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 403

def test_create_vpc_admin(user1, user2, login, member_factory, vpc_factory):
    """
    Try to create a VPC as an admin: must succeed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    member_factory('user1-default', user2, token1, is_admin=True)
    response = client.post('/api/0.1/vpcs/user1-default/', {'name':'tocreate'}, HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 201

def test_list_vpcs_no_authentication(user1):
    """
    Try to list VPCS without being authenticated:
    must failed.
    """
    client = APIClient()
    response = client.get('/api/0.1/vpcs/user1-default/')
    assert response.status_code == 403

def test_list_vpcs_authenticated(user1, login, vpc_factory):
    """
    Try to list VPCS being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.get('/api/0.1/vpcs/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 200
    assert response.json()['count'] == 1
    #
    vpc_factory('my_vpc', token, 'user1-default')
    response = client.get('/api/0.1/vpcs/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['count'] == 2
    assert sorted(response.json()['results'])[1]['name'] == 'my_vpc'
    assert sorted(response.json()['results'])[1]['deletable'] is True
    assert sorted(response.json()['results'])[1]['date_created']
    assert sorted(response.json()['results'])[1]['date_modified']

def test_list_vpcs_two_accounts(user1, user2, login, vpc_factory):
    """
    Given two accounts, list theirs VPCS : must only see their own.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    vpc_factory('user1', token1, 'user1-default')
    vpc_factory('again_user1', token1, 'user1-default')
    vpc_factory('user2', token2, 'user2-default')
    # User1 check
    response = client.get('/api/0.1/vpcs/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.json()['count'] == 3
    assert 'default' in [i['name'] for i in response.json()['results']]
    assert 'user1' in [i['name'] for i in response.json()['results']]
    assert 'again_user1' in [i['name'] for i in response.json()['results']]
    assert 'user2' not in [i['name'] for i in response.json()['results']]
    # User2 Check
    response = client.get('/api/0.1/vpcs/user2-default/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.json()['count'] == 2
    assert 'user1' not in [i['name'] for i in response.json()['results']]
    assert 'again_user1' not in [i['name'] for i in response.json()['results']]
    assert 'user2' in [i['name'] for i in response.json()['results']]
    assert 'default' in [i['name'] for i in response.json()['results']]

def test_list_filters(user1, login, vpc_factory):
    """
    Check that we can filter on the name and owner.
    """
    client = APIClient()
    token1 = login(user1)
    vpc_factory('user1', token1, 'user1-default')
    vpc_factory('againuser1', token1, 'user1-default')
    response = client.get('/api/0.1/vpcs/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.json()['count'] == 3
    # name filter
    response = client.get('/api/0.1/vpcs/user1-default/?name=user1', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.json()['count'] == 1
    response = client.get('/api/0.1/vpcs/user1-default/?name=xxxx', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.json()['count'] == 0

def test_detail_vpc_unauthenticated(user1, login, vpc_factory):
    """
    Try to  access to a detail of an VPC without being authenticated:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    vpc_factory('my_vpc', token, 'user1-default')
    response = client.get('/api/0.1/vpcs/user1-default/my_vpc/')
    assert response.status_code == 403

def test_detail_vpc_authenticated(user1, login, vpc_factory):
    """
    Try to access to a detail of an VPC being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    vpc_factory('my_vpc', token, 'user1-default')
    response = client.get('/api/0.1/vpcs/user1-default/my_vpc/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 200
    assert response.json()['name'] == 'my_vpc'
    assert response.json()['deletable'] is True
    assert response.json()['date_created']
    assert response.json()['date_modified']
    # Non existing
    response = client.get('/api/0.1/vpcs/user1-default/my_wrong_vpc/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 404

def test_detail_vpc_two_accounts(user1, user2, login, vpc_factory):
    """
    Accounts must only access of the details to their VPCs.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    vpc_factory('vpc1', token1, 'user1-default')
    vpc_factory('vpc2', token2, 'user2-default')
    ##
    response = client.get('/api/0.1/vpcs/user1-default/vpc1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 200
    response = client.get('/api/0.1/vpcs/user2-default/vpc2/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 403
    ##
    response = client.get('/api/0.1/vpcs/user1-default/vpc1/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 403
    response = client.get('/api/0.1/vpcs/user2-default/vpc2/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 200

def test_no_head_method(user1, login, vpc_factory):
    """
    Try to do a head on a VPC resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    vpc_factory('my_vpc', token, 'user1-default')
    response = client.head('/api/0.1/vpcs/user1-default/my_vpc/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 405

def test_no_put_method(user1, login, vpc_factory):
    """
    Try to do a PUT on a VPC resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    vpc_factory('my_vpc', token, 'user1-default')
    response = client.patch('/api/0.1/vpcs/user1-default/my_vpc/', {'name': 'myvpc'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 405

def test_no_patch_method(user1, login, vpc_factory):
    """
    Try to do a PATCH on a VPC resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    vpc_factory('my_vpc', token, 'user1-default')
    response = client.patch('/api/0.1/vpcs/user1-default/my_vpc/', {'name': 'myvpc'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 405

def test_delete_unauthenticated(user1, login, vpc_factory):
    """
    Try to delete a VPC without being authenticated:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    vpc_factory('my_vpc', token, 'user1-default')
    response = client.delete('/api/0.1/vpcs/user1-default/my_vpc/')
    assert response.status_code == 403
    ##
    response = client.delete('/api/0.1/vpcs/user1-default/my_wrong_vpc/')
    assert response.status_code == 403

def test_delete_authenticated(user1, login, vpc_factory):
    """
    Try to delete a VPC being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    vpc_factory('my_vpc', token, 'user1-default')
    response = client.get('/api/0.1/vpcs/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['count'] == 2
    ##
    response = client.delete('/api/0.1/vpcs/user1-default/my_vpc/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 204
    ##
    response = client.get('/api/0.1/vpcs/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['count'] == 1
    ##
    response = client.delete('/api/0.1/vpcs/user1-default/my_vpc/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 404

def test_delete_default_vpc(user1, login):
    """
    Try to delete its default VPC:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    response = client.delete('/api/0.1/vpcs/user1-default/default/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 403

def test_delete_vpc_not_admin(user1, user2, login, member_factory, vpc_factory):
    """
    Try to delete a VPC as a non admin: must failed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    member_factory('user1-default', user2, token1)
    vpc_factory('todelete', token1, 'user1-default')
    response = client.get('/api/0.1/vpcs/user1-default/todelete/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 200
    response = client.delete('/api/0.1/vpcs/user1-default/todelete/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 403

def test_delete_vpc_admin(user1, user2, login, member_factory, vpc_factory):
    """
    Try to delete a VPC as an admin: must succeed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    member_factory('user1-default', user2, token1, is_admin=True)
    vpc_factory('todelete', token1, 'user1-default')
    response = client.get('/api/0.1/vpcs/user1-default/todelete/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 200
    response = client.delete('/api/0.1/vpcs/user1-default/todelete/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 204

def test_delete_two_accounts(user1, user2, login, vpc_factory):
    """
    Accounts can only be able to delete their VPCs.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    vpc_factory('user1', token1, 'user1-default')
    vpc_factory('user2', token2, 'user2-default')
    ##
    response = client.delete('/api/0.1/vpcs/user1-default/user1/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 404
    response = client.delete('/api/0.1/vpcs/user2-default/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 404
    ##
    response = client.delete('/api/0.1/vpcs/user1-default/user1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 204
    response = client.delete('/api/0.1/vpcs/user2-default/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 204

def test_created_send_broker_message(broker_namespace_create, user1, login, vpc_factory):
    """
    When creating a vpc, a message must be send to the broker.
    """
    queue, _ = broker_namespace_create
    #consume default one
    msg = json.loads(next(queue.consume()).body)
    #
    token1 = login(user1)
    vpc_factory('vpc1', token1, 'user1-default')
    #
    msg = json.loads(next(queue.consume()).body)
    assert msg == {'namespace': 'user1-default-vpc1'}

def test_deleted_send_broker_message(broker_namespace_delete, user1, login, vpc_factory):
    """
    When deleting a vpc, a message must be send to the broker.
    """
    queue, _ = broker_namespace_delete
    client = APIClient()
    token1 = login(user1)
    vpc_factory('vpc1', token1, 'user1-default')
    client.delete('/api/0.1/vpcs/user1-default/vpc1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    #
    msg = json.loads(next(queue.consume()).body)
    assert msg == {'namespace': 'user1-default-vpc1'}
