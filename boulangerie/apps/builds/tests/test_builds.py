#-*- coding:utf-8 -*-
"""
Unit tests for builds.
"""
#pylint:disable=redefined-outer-name,wildcard-import,unused-wildcard-import,line-too-long,invalid-name,no-member,unused-import
import json
from rest_framework.test import APIClient
from .fixtures import *

def test_list_no_authenticated():
    """
    Try to list the builds of an organization without being authenticated:
    must failed.
    """
    client = APIClient()
    response = client.get('/api/0.1/builds/user1-default/')
    assert response.status_code == 403

def test_list_authenticated(user1, login, list_builds):
    """
    Try to list the builds of an organization being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.get('/api/0.1/builds/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 200
    assert response.json()['count'] == 2
    ##
    first = json.loads(response.json()['results'][0])
    second = json.loads(response.json()['results'][1])
    assert isinstance(first, dict)
    assert isinstance(second, dict)
    ##
    assert first['uid'] == 'c7c853961d9942ddb0b8619a8ae55408'
    ##
    assert second['uid'] == '3b73f69f3fb94f159d8a3230596c2e3b'

def test_list_authenticated_not_exist(user1, login):
    """
    Try to list the builds of an non existing organization being authenticated:
    must failed
    """
    client = APIClient()
    token = login(user1)
    response = client.get('/api/0.1/builds/user2-default/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 404

def test_detail_no_authenticated():
    """
    Try to detail a build of an organization without being authenticated:
    must failed.
    """
    client = APIClient()
    response = client.get('/api/0.1/builds/user1-default/3b73f69f3fb94f159d8a3230596c2e3b/')
    assert response.status_code == 403

def test_detail_authenticated(user1, login, detail_build):
    """
    Try to detail a build of an organization being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.get('/api/0.1/builds/user1-default/3b73f69f3fb94f159d8a3230596c2e3b/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 200
    assert response.json()['count'] == 8
    assert len(response.json()['results']) == 8

def test_detail_authenticated_invalid_uid(user1, login):
    """
    Try to detail a build of an organization with an invalid uid:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    response = client.get('/api/0.1/builds/user1-default/2/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 400

def test_detail_authenticated_orga_not_exist(user1, login):
    """
    Try to detail a build of a non existing organization being authenticated:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    response = client.get('/api/0.1/builds/idontexist/3b73f69f3fb94f159d8a3230596c2e3b/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 404

def test_detail_authenticated_not_exist(user1, login, detail_nobuild):
    """
    Try to detail a build of an existing organization being authenticated but with a non existing uid:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.get('/api/0.1/builds/user1-default/2550873c57cd46e6a164f3776be58cd1/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['count'] == 0
    assert not response.json()['results']
