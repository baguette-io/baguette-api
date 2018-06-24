#-*- coding:utf-8 -*-
"""
Signal handler for Quotas.
"""
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models.signals import post_save
from boulangerie.apps.accounts.models import Account
from boulangerie.apps.organizations.models import Organization
from .models import Quota

@receiver(post_save, sender=Account)
def default_quotas_account(sender, **kwargs):#pylint:disable=unused-argument
    """
    When creating an account,
    create the quotas.
    :param sender: The signal sender.
    :type sender: boulangerie.apps.accounts.models.Account
    :param kwargs: Context.
    :type kwargs: django.db.models.base.ModelBase
    :rtype:None
    """
    if kwargs.get('created'):
        owner = kwargs['instance'].username
        Quota.objects.create(key='max_keys',#pylint:disable=no-member
                             value=settings.QUOTAS['max_keys'],
                             owner=owner)
        Quota.objects.create(key='max_organizations',#pylint:disable=no-member
                             value=settings.QUOTAS['max_organizations'],
                             owner=owner)

@receiver(post_save, sender=Organization)
def default_quotas_organization(sender, **kwargs):#pylint:disable=unused-argument
    """
    When creating an organization,
    create the quotas.
    :param sender: The signal sender.
    :type sender: boulangerie.apps.organizations.models.Organization
    :param kwargs: Context.
    :type kwargs: django.db.models.base.ModelBase
    :rtype:None
    """
    if kwargs.get('created'):
        owner = kwargs['instance'].name
        Quota.objects.create(key='max_projects',#pylint:disable=no-member
                             value=settings.QUOTAS['max_projects'],
                             owner=owner)
        Quota.objects.create(key='max_vpcs',#pylint:disable=no-member
                             value=settings.QUOTAS['max_vpcs'],
                             owner=owner)
