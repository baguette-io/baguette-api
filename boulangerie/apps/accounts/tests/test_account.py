#-*-coding:utf-8 -*-
"""
Test module for account workflow.
"""
#pylint:disable=no-member
import decimal
import json
from rest_framework.test import APIClient
from .fixtures import *#pylint:disable=wildcard-import,unused-wildcard-import

def test_simple_creation():#pylint:disable=redefined-outer-name
    """
    Try to create an account:
        must succeed.
    Check the response body.
    """
    client = APIClient()
    body = {'username':'username',
            'password':'password',
            'confirm_password': 'password',
            'email': 'test_simple_creation@test.test',
           }
    response = client.post('/api/0.1/accounts/register/', body, format='json')
    assert response.status_code == 201
    result = response.json()
    assert result.has_key('account')
    assert result['account']['username'] == body['username']
    assert result['account']['email'] == body['email']
    assert not result['account'].get('password')
    assert not result['account'].get('confirm_password')
    assert result['account'].has_key('firstname')
    assert result['account'].has_key('lastname')


def test_creation_key(login):#pylint:disable=redefined-outer-name
    """
    When creating an user, a ssh key
    must be created automatically.
    """
    client = APIClient()
    body = {'username':'username',
            'password':'password',
            'confirm_password': 'password',
            'email': 'test_simple_creation@test.test',
           }
    result = client.post('/api/0.1/accounts/register/', body, format='json').json()
    assert result['key']['name'] == 'default'
    assert result['key']['private']
    assert result['key']['public'].startswith('ssh-rsa')
    assert result['key']['fingerprint'].startswith('MD5:')
    # Request also the /keys endpoint.
    token = login(body)
    response = client.get('/api/0.1/keys/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 200
    assert response.json()['count'] == 1
    key = response.json()['results'][0]
    assert key['name'] == result['key']['name']
    assert key['public'] == result['key']['public']
    assert key['fingerprint'] == result['key']['fingerprint']
    assert not key.has_key('private')

def test_creation_broker_message_key(broker_git_create_key, broker_namespace_create):
    """
    When creating an account, a message must be send to the broker to create a key.
    """
    #1. Create the broker queue
    queue, _ = broker_git_create_key
    queue2, _ = broker_namespace_create
    #2. Create the user
    client = APIClient()
    body = {'username':'username',
            'password':'password',
            'confirm_password': 'password',
            'email': 'test_simple_creation@test.test',
           }
    result = client.post('/api/0.1/accounts/register/', body, format='json').json()
    #3. Check
    msg = json.loads(next(queue.consume()).body)
    assert msg == {'user': 'username', 'key': result['key']['public'], 'user_creation': True, 'organization_creation': True, 'organization': 'username-default'}
    msg = json.loads(next(queue2.consume()).body)
    assert msg == {'namespace':'username-default-default'}

def test_creation_broker_message_vpc(broker_git_create_key, broker_namespace_create):
    """
    When creating an account, a message must be send to the broker to create the default vpc.
    """
    #1. Create the broker queue
    queue, _ = broker_git_create_key
    queue2, _ = broker_namespace_create
    #2. Create the user
    client = APIClient()
    body = {'username':'username',
            'password':'password',
            'confirm_password': 'password',
            'email': 'test_simple_creation@test.test',
           }
    result = client.post('/api/0.1/accounts/register/', body, format='json').json()
    #3. Check
    msg = json.loads(next(queue2.consume()).body)
    assert msg == {'namespace': 'username-default-default'}

def test_creation_quotas_set(login, broker_git_create_key, broker_namespace_create):#pylint:disable=redefined-outer-name
    """
    When creating an account, check that the quotas are created.
    """
    #1. Create the user
    queue, _ = broker_git_create_key
    queue2, _ = broker_namespace_create
    client = APIClient()
    body = {'username':'username',
            'password':'password',
            'confirm_password': 'password',
            'email': 'test_simple_creation@test.test',
           }
    client.post('/api/0.1/accounts/register/', body, format='json')
    #2. Check its quotas
    token = login(body)
    response = client.get('/api/0.1/quotas/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 200
    assert len(response.json()['results']) == 2
    quotas = {i['key']:i['value'] for i in response.json()['results']}
    assert decimal.Decimal(quotas['max_keys']) == 1000
    assert decimal.Decimal(quotas['max_organizations']) == 1000
