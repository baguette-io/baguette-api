#-*- coding:utf-8 -*-
"""
Fixtures for accounts.
"""
#pylint:disable=line-too-long
import pytest
from rest_framework.test import APIClient
from boulangerie.apps.accounts.models import Account as User

pytestmark = pytest.mark.django_db#pylint:disable=invalid-name

@pytest.fixture
def user_factory():
    """
    Create a dummy user.
    """
    def factory(name):
        infos = {'username':name, 'email':'%s@test.org' % name, 'password':'password'}
        created = User.objects.create_user(**infos)
        return infos
    return factory

@pytest.fixture
def user1():
    """
    Create a dummy user.
    """
    infos = {'username':'user1', 'email':'user1@test.org', 'password':'password'}
    created = User.objects.create_user(**infos)
    return infos

@pytest.fixture
def user2():
    """
    Create another dummy user.
    """
    infos = {'username':'user2', 'email':'user2@test.org', 'password':'password'}
    User.objects.create_user(**infos)
    return infos

@pytest.fixture
def user3():
    """
    Create another dummy user.
    """
    infos = {'username':'user3', 'email':'user3@test.org', 'password':'password'}
    User.objects.create_user(**infos)
    return infos

@pytest.fixture
def admin1():
    """
    Create an admin user.
    """
    infos = {'username':'admin1', 'email':'admin1@test.org', 'password':'password'}
    User.objects.create_superuser(**infos)
    return infos

@pytest.fixture
def login():
    """
    Log the specified user.
    Returns the JWT token.
    """
    def factory(user):
        """
        Take in parameter the user infos.
        """
        client = APIClient()
        response = client.post('/api/0.1/accounts/login/', {'username':user['username'], 'password':user['password']}, format='json')
        return response.json()["token"]#pylint:disable=no-member
    return factory
