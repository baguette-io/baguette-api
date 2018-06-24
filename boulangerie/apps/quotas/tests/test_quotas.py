#-*- coding:utf-8 -*-
"""
Unit tests for Quotas.
"""
#pylint:disable=redefined-outer-name,wildcard-import,unused-wildcard-import,line-too-long,invalid-name,no-member,unused-import
import decimal
from rest_framework.test import APIClient
from boulangerie.apps.projects.tests.fixtures import project_factory
from .fixtures import *

def test_list_no_authenticated():
    """
    Try to list quotas without being authenticated:
    must failed.
    """
    client = APIClient()
    response = client.get('/api/0.1/quotas/')
    assert response.status_code == 403

def test_list_authenticated_account(user1, login):
    """
    Try to list quotas being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.get('/api/0.1/quotas/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 200
    assert len(response.json()['results']) == 2
    quotas = {i['key']:i['value'] for i in response.json()['results']}
    assert decimal.Decimal(quotas['max_keys']) == 1000
    assert decimal.Decimal(quotas['max_organizations']) == 1000

def test_list_authenticated_organization(user1, login):
    """
    Try to list quotas being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.get('/api/0.1/quotas/', {'organization':'user1-default'}, HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 200
    assert len(response.json()['results']) == 2
    quotas = {i['key']:i['value'] for i in response.json()['results']}
    assert decimal.Decimal(quotas['max_vpcs']) == 1000
    assert decimal.Decimal(quotas['max_projects']) == 1000

def test_quota_max_keys(user1, quota_factory, login, pubkey1, pubkey2):
    """
    Check that when the quota is reached
    the user cannot creates more keys.
    """
    quota_factory(user1['username'], 'max_keys', 1)
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/keys/',
                           {'name': 'my_key', 'public':pubkey1},
                           format='json',
                           HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    #
    response = client.post('/api/0.1/keys/',
                           {'name': 'my_second_key', 'public':pubkey2},
                           format='json',
                           HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 403
    #Still can delete&co
    response = client.delete('/api/0.1/keys/my_key/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 204


def test_quota_max_projects(user1, quota_factory, login):
    """
    Check that when the quota is reached
    the user cannot creates more projects.
    """
    quota_factory('user1-default', 'max_projects', 1)
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/projects/user1-default/',
                           {'name': 'my_project', 'repo': 'my_repo'},
                           format='json',
                           HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    response = client.post('/api/0.1/projects/user1-default/',
                           {'name': 'my_second_project', 'repo': 'my_second_repo'},
                           format='json',
                           HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 403
    #Still can delete&co
    response = client.delete('/api/0.1/projects/user1-default/my_project/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 204

def test_quota_max_vpcs(user1, quota_factory, login):
    """
    Check that when the quota is reached
    the user cannot creates more vpcs.
    """
    quota_factory('user1-default', 'max_vpcs', 2)
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/vpcs/user1-default/',
                           {'name': 'my_vpc'},
                           format='json',
                           HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    response = client.post('/api/0.1/vpcs/user1-default/',
                           {'name': 'my_second_vpcs'},
                           format='json',
                           HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 403
    #Still can delete&co
    response = client.delete('/api/0.1/vpcs/user1-default/my_vpc/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 204

def test_quota_max_organizations(user1, quota_factory, login):
    """
    Check that when the quota is reached
    the user cannot creates more organizations.
    """
    quota_factory(user1['username'], 'max_organizations', 2)
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/organizations/',
                           {'name': 'my_orga'},
                           format='json',
                           HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    response = client.post('/api/0.1/organizations/',
                           {'name': 'my_second_orga'},
                           format='json',
                           HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 403
    #Still can delete&co
    response = client.delete('/api/0.1/organizations/my_orga/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 204

def test_no_post_method(user1, login):
    """
    Try to do a head on a quota resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/quotas/', {'key':'key', 'value': 'value'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 403

def test_no_put_method(user1, login):
    """
    Try to do a PUT on a quota resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    response = client.put('/api/0.1/quotas/', {'key':'max_keys', 'value': '1'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 403
    response = client.put('/api/0.1/quotas/max_keys/', {'key':'max_keys', 'value': '1'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 404

def test_no_patch_method(user1, login):
    """
    Try to do a PATCH on a quota resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    response = client.patch('/api/0.1/quotas/', {'key':'max_keys', 'value': '1'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 403
    response = client.patch('/api/0.1/quotas/max_keys/', {'value': '1'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 404

def test_no_delete_method(user1, login):
    """
    Try to do a DELETE on a quota resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    response = client.delete('/api/0.1/quotas/', format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 403
    response = client.delete('/api/0.1/quotas/max_keys/', format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 404
