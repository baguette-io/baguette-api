#-*- coding:utf-8 -*-
"""
Signal handler for organizations.
"""
import boulangerie.broker
import signal_disabler
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from boulangerie.apps.accounts.models import Account
from .models import Member, Organization

@receiver(post_save, sender=Account)
def default_organization(sender, **kwargs):#pylint:disable=unused-argument
    """
    When creating an account,
    create the default organization.
    :param sender: The signal sender.
    :type sender: boulangerie.apps.accounts.models.Account
    :param kwargs: Context.
    :type kwargs: django.db.models.base.ModelBase
    :rtype:None
    """
    if kwargs.get('created'):
        account = kwargs['instance'].username
        orga = Organization.objects.create(name='{}-default'.format(account), description='default', deletable=False)
        with signal_disabler.disable():
            Member.objects.create(account=account, organization=orga, is_owner=True, is_admin=True)#pylint:disable=no-member

@receiver(post_save, sender=Member)
def create_member(sender, instance, **kwargs):#pylint:disable=unused-argument
    """
    When adding a member to an organization
    we need to send a message to our broker.
    :param sender: The signal sender model class.
    :type sender: boulangerie.apps.projects.models.Member
    :param instance: The signal sender instance.
    :type instance: boulangerie.apps.projects.models.Member
    :param kwargs: Context.
    :type kwargs: django.db.models.base.ModelBase
    :rtype:None
    """
    if kwargs.get('created'):
        payload = {'organization': instance.organization.name, 'account': instance.account}
        boulangerie.broker.send(payload, 'create-member', 'git')

@receiver(post_delete, sender=Member)
def delete_member(sender, instance, **kwargs):#pylint:disable=unused-argument
    """
    When deleting a member from an organization,
    we need to send a message to our broker.
    :param sender: The signal sender.
    :type sender: boulangerie.apps.projects.models.Member
    :param instance: The signal sender instance.
    :type instance: boulangerie.apps.projects.models.Member
    :param kwargs: Context.
    :type kwargs: django.db.models.base.ModelBase
    :rtype:None
    """
    payload = {'organization': instance.organization.name, 'account': instance.account}
    boulangerie.broker.send(payload, 'delete-member', 'git')

@receiver(post_delete, sender=Organization)
def delete_organization(sender, instance, **kwargs):#pylint:disable=unused-argument
    """
    When deleting a member from an organization,
    we need to send a message to our broker.
    :param sender: The signal sender.
    :type sender: boulangerie.apps.projects.models.Organization
    :param instance: The signal sender instance.
    :type instance: boulangerie.apps.projects.models.Organization
    :param kwargs: Context.
    :type kwargs: django.db.models.base.ModelBase
    :rtype:None
    """
    payload = {'organization': instance.name}
    boulangerie.broker.send(payload, 'delete-organization', 'git')
