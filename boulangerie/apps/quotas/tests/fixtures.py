#-*- coding:utf-8 -*-
"""
Fixtures for the quotas tests.
"""
#pylint:disable=wildcard-import,unused-wildcard-import,line-too-long
from django.contrib.contenttypes.models import ContentType
from boulangerie.apps.accounts.tests.fixtures import *
from boulangerie.apps.keys.tests.fixtures import pubkey1, pubkey2#pylint:disable=unused-import
from boulangerie.apps.quotas.models import Quota


@pytest.fixture
def quota_factory():
    """
    Quota factory: Update current quotas.
    """
    def factory(account, key, value):
        """
        Takes 3 parameters:
        the users, its quota, and its new threshold.
        """
        current = Quota.objects.get(owner=account, key=key)#pylint:disable=no-member
        current.value = value
        current.save()
    return factory
