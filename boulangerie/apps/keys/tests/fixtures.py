#-*- coding:utf-8 -*-
"""
Fixtures for the keys tests.
"""
#pylint:disable=wildcard-import,unused-wildcard-import,line-too-long
from Crypto.PublicKey import RSA
from boulangerie.apps.accounts.tests.fixtures import *

@pytest.fixture
def pubkey1():
    """
    Dummy public key.
    """
    return RSA.generate(1024).publickey().exportKey('OpenSSH')

@pytest.fixture
def pubkey2():
    """
    Another dummy public key.
    """
    return RSA.generate(1024).publickey().exportKey('OpenSSH')

@pytest.fixture
def pubkey3():
    """
    Another another dummy public key.
    """
    return RSA.generate(1024).publickey().exportKey('OpenSSH')

@pytest.fixture()
def key_factory():
    """
    key factory.
    """
    def factory(name, token, pubkey):
        """
        Takes the key name, token and pubkey.
        """
        client = APIClient()
        response = client.post('/api/0.1/keys/', {'name': name, 'public':pubkey}, format='json', HTTP_AUTHORIZATION='JWT {}'.format(token))
        assert response.status_code == 201#pylint:disable=no-member
    return factory
