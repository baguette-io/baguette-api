#-*- coding:utf-8 -*-
"""
Unit tests for the SSH keys.
"""
#pylint:disable=redefined-outer-name,wildcard-import,unused-wildcard-import,line-too-long,invalid-name,no-member
import json
from rest_framework.test import APIClient
from .fixtures import *

def test_creation_no_authenticated():
    """
    Try to create a key without being authenticated:
    must failed.
    """
    client = APIClient()
    response = client.post('/api/0.1/keys/', {'name': 'my_key'}, format='json')
    assert response.status_code == 403

def test_creation_authenticated(user1, login, pubkey1):
    """
    Try to create a key being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/keys/', {'name': 'my_key', 'public':pubkey1}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201

def test_creation_authenticated_specified_fingerprint(user1, login, pubkey1):
    """
    Try to create a key being authenticated and specifying a fingerprint:
    must succeed and the fingerprint get ignored.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/keys/', {'name': 'my_key', 'public':pubkey1, 'fingerprint': 'toto'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    assert response.json()['fingerprint'].startswith('MD5:')

def test_creation_authenticated_invalid_public(user1, login):
    """
    Try to create a key being authenticated and specifying a wrong public key:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/keys/', {'name': 'my_key', 'public':'non_pub_key'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 400

def test_creation_same_name_error(user1, login, pubkey1):
    """
    Try to create two keys with the same user and the same name:
    must failed the second time.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/keys/', {'name': 'my_key', 'public':pubkey1}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    ##
    response = client.post('/api/0.1/keys/', {'name': 'my_key', 'public':pubkey1}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 400

def test_creation_same_public_error(user1, login, pubkey1):
    """
    Try to create two keys with the same user and the same public key:
    must failed the second time.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/keys/', {'name': 'my_key', 'public':pubkey1}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    ##
    response = client.post('/api/0.1/keys/', {'name': 'my_other_key', 'public':pubkey1}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 400

def test_creation_same_name_two_users(user1, user2, login, pubkey1, pubkey2):
    """
    Try to create two keys with the same name using two different users:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/keys/', {'name': 'my_key', 'public':pubkey1}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    ##
    token = login(user2)
    response = client.post('/api/0.1/keys/', {'name': 'my_key', 'public':pubkey2}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201

def test_creation_same_public_two_users(user1, user2, login, pubkey1):
    """
    Try to create two keys with the same public key using two different users:
    must failed the second time.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/keys/', {'name': 'my_key', 'public':pubkey1}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    ##
    token = login(user2)
    response = client.post('/api/0.1/keys/', {'name': 'my_key', 'public':pubkey1}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 400

def test_list_keys_no_authentication():
    """
    Try to list keys without being authenticated:
    must failed.
    """
    client = APIClient()
    response = client.get('/api/0.1/keys/')
    assert response.status_code == 403

def test_list_keys_authenticated(user1, login, key_factory, pubkey1):
    """
    Try to list keys being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.get('/api/0.1/keys/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 200
    assert response.json()['count'] == 0
    #
    key_factory('my_key', token, pubkey1)
    response = client.get('/api/0.1/keys/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['count'] == 1
    assert response.json()['results'][0]['name'] == 'my_key'
    assert response.json()['results'][0]['date_created']
    assert response.json()['results'][0]['date_modified']
    assert response.json()['results'][0]['fingerprint'].startswith('MD5:')
    assert response.json()['results'][0]['public'] == pubkey1

def test_list_keys_two_accounts(user1, user2, login, key_factory, pubkey1, pubkey2, pubkey3):
    """
    Given two accounts, list theirs keys : must only see their own.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    key_factory('user1', token1, pubkey1)
    key_factory('again_user1', token1, pubkey2)
    key_factory('user2', token2, pubkey3)
    # User1 check
    response = client.get('/api/0.1/keys/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.json()['count'] == 2
    assert 'user1' in [i['name'] for i in response.json()['results']]
    assert 'again_user1' in [i['name'] for i in response.json()['results']]
    assert 'user2' not in [i['name'] for i in response.json()['results']]
    # User2 Check
    response = client.get('/api/0.1/keys/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.json()['count'] == 1
    assert 'user1' not in [i['name'] for i in response.json()['results']]
    assert 'again_user1' not in [i['name'] for i in response.json()['results']]
    assert 'user2' in [i['name'] for i in response.json()['results']]

def test_detail_key_unauthenticated(user1, login, key_factory, pubkey1):
    """
    Try to  access to a detail of an key without being authenticated:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    key_factory('my_key', token, pubkey1)
    response = client.get('/api/0.1/keys/my_key/')
    assert response.status_code == 403

def test_detail_key_authenticated(user1, login, key_factory, pubkey1):
    """
    Try to access to a detail of an key being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    key_factory('my_key', token, pubkey1)
    response = client.get('/api/0.1/keys/my_key/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 200
    assert response.json()['name'] == 'my_key'
    assert response.json()['date_created']
    assert response.json()['date_modified']
    assert response.json()['fingerprint'].startswith('MD5:')
    assert response.json()['public'] == pubkey1
    # Non existing
    response = client.get('/api/0.1/keys/my_wrong_key/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 404

def test_detail_key_two_accounts(user1, user2, login, key_factory, pubkey1, pubkey2):
    """
    Accounts must only access of the details to their keys.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    key_factory('key1', token1, pubkey1)
    key_factory('key2', token2, pubkey2)
    ##
    response = client.get('/api/0.1/keys/key1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 200
    response = client.get('/api/0.1/keys/key2/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 404
    ##
    response = client.get('/api/0.1/keys/key1/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 404
    response = client.get('/api/0.1/keys/key2/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 200

def test_no_head_method(user1, login, key_factory, pubkey1):
    """
    Try to do a head on a key resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    key_factory('my_key', token, pubkey1)
    response = client.head('/api/0.1/keys/my_key/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 405

def test_no_put_method(user1, login, key_factory, pubkey1):
    """
    Try to do a PUT on a key resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    key_factory('my_key', token, pubkey1)
    response = client.patch('/api/0.1/keys/my_key/', {'name': 'mykey'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 405

def test_no_patch_method(user1, login, key_factory, pubkey1):
    """
    Try to do a PATCH on a key resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    key_factory('my_key', token, pubkey1)
    response = client.patch('/api/0.1/keys/my_key/', {'name': 'mykey'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 405

def test_delete_unauthenticated(user1, login, key_factory, pubkey1):
    """
    Try to delete a key without being authenticated:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    key_factory('my_key', token, pubkey1)
    response = client.delete('/api/0.1/keys/my_key/')
    assert response.status_code == 403
    ##
    response = client.delete('/api/0.1/keys/my_wrong_key/')
    assert response.status_code == 403

def test_delete_authenticated(user1, login, key_factory, pubkey1):
    """
    Try to delete a key being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    key_factory('my_key', token, pubkey1)
    response = client.get('/api/0.1/keys/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['count'] == 1
    ##
    response = client.delete('/api/0.1/keys/my_key/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 204
    ##
    response = client.get('/api/0.1/keys/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['count'] == 0
    ##
    response = client.delete('/api/0.1/keys/my_key/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 404

def test_delete_two_accounts(user1, user2, login, key_factory, pubkey1, pubkey2):
    """
    Accounts can only be able to delete their keys.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    key_factory('user1', token1, pubkey1)
    key_factory('user2', token2, pubkey2)
    ##
    response = client.delete('/api/0.1/keys/user1/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 404
    response = client.delete('/api/0.1/keys/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 404
    ##
    response = client.delete('/api/0.1/keys/user1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 204
    response = client.delete('/api/0.1/keys/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 204

def test_created_send_broker_message(broker_git_create_key, user1, login, key_factory, pubkey1):
    """
    When creating a key, a message must be send to the broker.
    """
    queue, _ = broker_git_create_key
    token1 = login(user1)
    key_factory('key1', token1, pubkey1)
    #
    msg = json.loads(next(queue.consume()).body)
    assert msg == {'user': 'user1', 'key': pubkey1}

def test_deleted_send_broker_message(broker_git_delete_key, user1, login, key_factory, pubkey1):
    """
    When deleting a key, a message must be send to the broker.
    """
    queue, _ = broker_git_delete_key
    client = APIClient()
    token1 = login(user1)
    key_factory('key1', token1, pubkey1)
    client.delete('/api/0.1/keys/key1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    #
    msg = json.loads(next(queue.consume()).body)
    assert msg == {'user': 'user1', 'key': pubkey1}
