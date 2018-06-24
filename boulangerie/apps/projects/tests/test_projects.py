#-*- coding:utf-8 -*-
"""
Unit tests for projects.
"""
#pylint:disable=redefined-outer-name,wildcard-import,unused-wildcard-import,line-too-long,invalid-name,no-member,unused-import
import json
from rest_framework.test import APIClient
from boulangerie.apps.vpcs.tests.fixtures import vpc_factory
from .fixtures import *

def test_creation_no_authenticated(user1):
    """
    Try to create a project without being authenticated:
    must failed.
    """
    client = APIClient()
    response = client.post('/api/0.1/projects/user1-default/', {'name': 'my_project'}, format='json')
    assert response.status_code == 403

def test_creation_authenticated(user1, login):
    """
    Try to create a project being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/projects/user1-default/', {'name': 'my_project'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201

def test_creation_authenticated_repo_ignored(user1, login):
    """
    Try to create a project being authenticated and with repo as parameter:
    must succeed and repo is ignored.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/projects/user1-default/', {'name': 'my_project', 'repo': 'my_repo'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    assert response.json()['uri'] == 'git@git.baguette.io:user1-default.my_project.git'

def test_creation_same_name_error(user1, login):
    """
    Try to create two projects with the same user and the same name:
    must failed the second time.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/projects/user1-default/', {'name': 'my_project'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    ##
    response = client.post('/api/0.1/projects/user1-default/', {'name': 'my_project'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 400

def test_creation_same_name_two_users(user1, user2, login):
    """
    Try to create two projects with the same name using two different users:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/projects/user1-default/', {'name': 'my_project'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201
    ##
    token = login(user2)
    response = client.post('/api/0.1/projects/user2-default/', {'name': 'my_project'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 201

def test_create_project_non_deletable(user1, login):
    """
    Try to create a non deletable project : must succeed.
    """
    client = APIClient()
    token1 = login(user1)
    response = client.post('/api/0.1/projects/user1-default/', {'name':'nondeletable', 'deletable':False}, HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 201
    response = client.get('/api/0.1/projects/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.json()['count'] == 1
    assert response.json()['results'][0]['name'] == 'nondeletable'
    assert response.json()['results'][0]['deletable'] is False

def test_create_project_admin(user1, user2, login, member_factory):
    """
    Try to create a project as an admin: must succeed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    member_factory('user1-default', user2, token1, is_admin=True)
    response = client.post('/api/0.1/projects/user1-default/', {'name':'tocreate'}, HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 201

def test_create_project_non_admin(user1, user2, login, member_factory):
    """
    Try to create a project as a non admin: must failed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    member_factory('user1-default', user2, token1, is_admin=False)
    response = client.post('/api/0.1/projects/user1-default/', {'name':'tocreate'}, HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 403

def test_list_projects_no_authentication(user1):
    """
    Try to list projects without being authenticated:
    must failed.
    """
    client = APIClient()
    response = client.get('/api/0.1/projects/user1-default/')
    assert response.status_code == 403

def test_list_projects_authenticated(user1, login, project_factory):
    """
    Try to list projects being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    response = client.get('/api/0.1/projects/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 200
    assert response.json()['count'] == 0
    #
    project_factory('my_project', token, 'user1-default')
    response = client.get('/api/0.1/projects/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['count'] == 1
    assert response.json()['results'][0]['name'] == 'my_project'
    assert response.json()['results'][0]['uri'] == 'git@git.baguette.io:user1-default.my_project.git'
    assert response.json()['results'][0]['date_created']
    assert response.json()['results'][0]['date_modified']
    assert response.json()['results'][0]['deletable'] is True

def test_list_projects_two_accounts(user1, user2, login, project_factory):
    """
    Given two accounts, list theirs projects : must only see their own.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    project_factory('user1', token1, 'user1-default')
    project_factory('again_user1', token1, 'user1-default')
    project_factory('user2', token2, 'user2-default')
    # User1 check
    response = client.get('/api/0.1/projects/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.json()['count'] == 2
    assert 'user1' in [i['name'] for i in response.json()['results']]
    assert 'again_user1' in [i['name'] for i in response.json()['results']]
    assert 'user2' not in [i['name'] for i in response.json()['results']]
    # User2 Check
    response = client.get('/api/0.1/projects/user2-default/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.json()['count'] == 1
    assert 'user1' not in [i['name'] for i in response.json()['results']]
    assert 'again_user1' not in [i['name'] for i in response.json()['results']]
    assert 'user2' in [i['name'] for i in response.json()['results']]

def test_detail_project_unauthenticated(user1, login, project_factory):
    """
    Try to  access to a detail of an project without being authenticated:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    project_factory('my_project', token, 'user1-default')
    response = client.get('/api/0.1/projects/user1-default/my_project/')
    assert response.status_code == 403

def test_detail_project_authenticated(user1, login, project_factory):
    """
    Try to access to a detail of an project being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    project_factory('my_project', token, 'user1-default')
    response = client.get('/api/0.1/projects/user1-default/my_project/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 200
    assert response.json()['name'] == 'my_project'
    assert response.json()['uri'] == 'git@git.baguette.io:user1-default.my_project.git'
    assert response.json()['date_created']
    assert response.json()['date_modified']
    # Non existing
    response = client.get('/api/0.1/projects/user1-default/my_wrong_project/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 404

def test_detail_project_two_accounts(user1, user2, login, project_factory):
    """
    Accounts must only access of the details to their projects.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    project_factory('project1', token1, 'user1-default')
    project_factory('project2', token2, 'user2-default')
    ##
    response = client.get('/api/0.1/projects/user1-default/project1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 200
    response = client.get('/api/0.1/projects/user2-default/project2/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 403
    ##
    response = client.get('/api/0.1/projects/user1-default/project1/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 403
    response = client.get('/api/0.1/projects/user2-default/project2/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 200

def test_no_head_method(user1, login, project_factory):
    """
    Try to do a head on a project resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    project_factory('my_project', token, 'user1-default')
    response = client.head('/api/0.1/projects/user1-default/my_project/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 405

def test_no_put_method(user1, login, project_factory):
    """
    Try to do a PUT on a project resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    project_factory('my_project', token, 'user1-default')
    response = client.patch('/api/0.1/projects/user1-default/my_project/', {'name': 'myproject'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 405

def test_no_patch_method(user1, login, project_factory):
    """
    Try to do a PATCH on a project resource:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    project_factory('my_project', token, 'user1-default')
    response = client.patch('/api/0.1/projects/user1-default/my_project/', {'name': 'myproject'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 405

def test_delete_unauthenticated(user1, login, project_factory):
    """
    Try to delete a project without being authenticated:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    project_factory('my_project', token, 'user1-default')
    response = client.delete('/api/0.1/projects/user1-default/my_project/')
    assert response.status_code == 403
    ##
    response = client.delete('/api/0.1/projects/user1-default/my_wrong_project/')
    assert response.status_code == 403

def test_delete_authenticated(user1, login, project_factory):
    """
    Try to delete a project being authenticated:
    must succeed.
    """
    client = APIClient()
    token = login(user1)
    project_factory('my_project', token, 'user1-default')
    response = client.get('/api/0.1/projects/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['count'] == 1
    ##
    response = client.delete('/api/0.1/projects/user1-default/my_project/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 204
    ##
    response = client.get('/api/0.1/projects/user1-default/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.json()['count'] == 0
    ##
    response = client.delete('/api/0.1/projects/user1-default/my_project/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 404

def test_delete_non_deletable(user1, login, project_factory):
    """
    Try to delete its default VPC:
    must failed.
    """
    client = APIClient()
    token = login(user1)
    project_factory('my_project', token, 'user1-default', False)
    response = client.delete('/api/0.1/projects/user1-default/my_project/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    assert response.status_code == 403

def test_delete_project_non_admin(user1, user2, login, member_factory, project_factory):
    """
    Try to delete a project as a non admin: must failed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    member_factory('user1-default', user2, token1)
    project_factory('todelete', token1, 'user1-default')
    response = client.get('/api/0.1/projects/user1-default/todelete/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 200
    response = client.delete('/api/0.1/projects/user1-default/todelete/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 403

def test_delete_project_admin(user1, user2, login, member_factory, project_factory):
    """
    Try to delete a project as an admin: must succeed.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    member_factory('user1-default', user2, token1, is_admin=True)
    project_factory('todelete', token1, 'user1-default')
    response = client.get('/api/0.1/projects/user1-default/todelete/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 200
    response = client.delete('/api/0.1/projects/user1-default/todelete/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 204

def test_delete_two_accounts(user1, user2, login, project_factory):
    """
    Accounts can only be able to delete their projects.
    """
    client = APIClient()
    token1 = login(user1)
    token2 = login(user2)
    project_factory('user1', token1, 'user1-default')
    project_factory('user2', token2, 'user2-default')
    ##
    response = client.delete('/api/0.1/projects/user1-default/user1/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 404
    response = client.delete('/api/0.1/projects/user2-default/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 404
    ##
    response = client.delete('/api/0.1/projects/user1-default/user1/', HTTP_AUTHORIZATION='JWT {}'.format(token1))
    assert response.status_code == 204
    response = client.delete('/api/0.1/projects/user2-default/user2/', HTTP_AUTHORIZATION='JWT {}'.format(token2))
    assert response.status_code == 204

def test_created_send_broker_message(broker_git_create_repo, user1, login):
    """
    When creating a project, a message must be send to the broker.
    """
    queue, _ = broker_git_create_repo
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/projects/user1-default/', {'name': 'project1'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    #
    msg = json.loads(next(queue.consume()).body)
    assert msg == {'repo': 'user1-default.project1', 'organization': 'user1-default'}

def test_deleted_send_broker_message(broker_git_delete_repo, user1, login):
    """
    When deleting a project, a message must be send to the broker.
    """
    client = APIClient()
    token = login(user1)
    response = client.post('/api/0.1/projects/user1-default/', {'name': 'project1'}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
    #
    queue, _ = broker_git_delete_repo
    client.delete('/api/0.1/projects/user1-default/project1/', HTTP_AUTHORIZATION='JWT {}'.format(token))
    #
    msg = json.loads(next(queue.consume()).body)
    assert msg == {'repo': 'user1-default.project1'}
