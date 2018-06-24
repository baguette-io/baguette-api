#-*- coding:utf-8 -*-
"""
Fixtures for the Project tests.
"""
#pylint:disable=wildcard-import,unused-wildcard-import,line-too-long
from boulangerie.apps.accounts.tests.fixtures import *
from boulangerie.apps.organizations.tests.fixtures import member_factory

@pytest.fixture()
def project_factory():
    """
    Project factory.
    """
    def factory(name, token, organization, deletable=True):
        """
        Takes the Project name, token.
        """
        client = APIClient()
        args = {'name':name, 'deletable':deletable}
        response = client.post('/api/0.1/projects/{}/'.format(organization), args, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
        assert response.status_code == 201#pylint:disable=no-member
    return factory
