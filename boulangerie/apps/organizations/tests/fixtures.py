#-*- coding:utf-8 -*-
"""
Fixtures for the Organization tests.
"""
#pylint:disable=wildcard-import,unused-wildcard-import,line-too-long
from boulangerie.apps.accounts.tests.fixtures import *

@pytest.fixture()
def orga_factory():
    """
    Organization factory.
    """
    def factory(name, token, description=None, deletable=True):
        """
        Takes the Project name, token.
        """
        client = APIClient()
        args = {'name':name, 'description':description, 'deletable':deletable}
        response = client.post('/api/0.1/organizations/', args, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
        assert response.status_code == 201#pylint:disable=no-member
    return factory

@pytest.fixture()
def invit_factory():
    """
    Invitation factory.
    """
    def factory(organization, account, token):
        """
        Takes the organization, account and token.
        """
        client = APIClient()
        args = {'organization':organization, 'account': account}
        response = client.post('/api/0.1/invitations/', args, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
        assert response.status_code == 201#pylint:disable=no-member
    return factory

@pytest.fixture()
def member_factory(login):
    """
    Member factory.
    """
    def factory(organization, account, token, is_admin=False):
        """
        Takes the organization, account and token.
        """
        #Invit
        client = APIClient()
        args = {'organization':organization, 'account': account['username']}
        response = client.post('/api/0.1/invitations/', args, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
        assert response.status_code == 201#pylint:disable=no-member
        #Accept
        token2 = login(account)
        response = client.put('/api/0.1/invitations/{}/'.format(organization), args, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token2))
        assert response.status_code == 204
        #Admin
        if is_admin:
            response = client.patch('/api/0.1/members/{}/'.format(organization),{'account':'user2', 'is_admin':True}, HTTP_AUTHORIZATION='JWT {}'.format(token))
            assert response.status_code == 204
    return factory
