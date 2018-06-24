#-*- coding:utf-8 -*-
"""
Signal handler for VPCs.
"""
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import boulangerie.broker
from boulangerie.apps.organizations.models import Organization
from .models import VPC

@receiver(post_save, sender=Organization)
def default_vpc(sender, **kwargs):#pylint:disable=unused-argument
    """
    When creating an account,
    create a default VPC, non deletable.
    :param sender: The signal sender.
    :type sender: boulangerie.apps.accounts.models.Account
    :param kwargs: Context.
    :type kwargs: django.db.models.base.ModelBase
    :rtype:None
    """
    if kwargs.get('created'):
        owner = kwargs['instance'].name
        VPC.objects.create(name='default', owner=owner, deletable=False)#pylint:disable=no-member

@receiver(post_save, sender=VPC)
def create_vpc(sender, instance, **kwargs):#pylint:disable=unused-argument
    """
    When creating a vpc,
    we need to send a message to our broker.
    :param sender: The signal sender model class.
    :type sender: boulangerie.apps.vpcs.models.VPC
    :param instance: The signal sender instance.
    :type instance: boulangerie.apps.vpcs.models.VPC
    :param kwargs: Context.
    :type kwargs: django.db.models.base.ModelBase
    :rtype:None
    """
    if kwargs.get('created'):
        payload = {'namespace':'{0}-{1}'.format(instance.owner, instance.name)}
        boulangerie.broker.send(payload, 'create', 'namespace')

@receiver(post_delete, sender=VPC)
def delete_vpc(sender, instance, **kwargs):#pylint:disable=unused-argument
    """
    When deleting a vpc,
    we need to send a message to our broker.
    :param sender: The signal sender.
    :type sender: boulangerie.apps.vpcs.models.VPC
    :param instance: The signal sender instance.
    :type instance: boulangerie.apps.vpcs.models.VPC
    :param kwargs: Context.
    :type kwargs: django.db.models.base.ModelBase
    :rtype:None
    """
    payload = {'namespace':'{0}-{1}'.format(instance.owner, instance.name)}
    boulangerie.broker.send(payload, 'delete', 'namespace')
