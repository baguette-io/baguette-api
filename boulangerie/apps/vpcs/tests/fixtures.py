#-*- coding:utf-8 -*-
"""
Fixtures for the VPC tests.
"""
#pylint:disable=wildcard-import,unused-wildcard-import,line-too-long
from boulangerie.apps.accounts.tests.fixtures import *
from boulangerie.apps.organizations.tests.fixtures import member_factory


@pytest.fixture()
def vpc_factory():
    """
    VPC factory.
    """
    def factory(name, token, organization):
        """
        Takes the VPC name, token.
        """
        client = APIClient()
        response = client.post('/api/0.1/vpcs/{}/'.format(organization), {'name': name}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
        assert response.status_code == 201#pylint:disable=no-member
    return factory
