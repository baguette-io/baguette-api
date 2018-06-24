#-*- coding:utf-8 -*-
"""
Signal handler for keys.
"""
import boulangerie.broker
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from .models import SSHKey

@receiver(post_save, sender=SSHKey)
def create_key(sender, instance, **kwargs):#pylint:disable=unused-argument
    """
    When creating a key,
    we need to send a message to our broker.
    :param sender: The signal sender model class.
    :type sender: boulangerie.apps.projects.models.SSHKey
    :param instance: The signal sender instance.
    :type instance: boulangerie.apps.projects.models.SSHKey
    :param kwargs: Context.
    :type kwargs: django.db.models.base.ModelBase
    :rtype:None
    """
    if kwargs.get('created'):
        payload = {'key': instance.public, 'user': instance.owner}
        if hasattr(instance, 'user_creation'):
            payload['user_creation'] = instance.user_creation
        if hasattr(instance, 'organization_creation'):
            payload['organization_creation'] = instance.organization_creation
            payload['organization'] = '{0}-default'.format(instance.owner)
        boulangerie.broker.send(payload, 'create-key', 'git')

@receiver(post_delete, sender=SSHKey)
def delete_key(sender, instance, **kwargs):#pylint:disable=unused-argument
    """
    When deleting a key,
    we need to send a message to our broker.
    :param sender: The signal sender.
    :type sender: boulangerie.apps.projects.models.SSHKey
    :param instance: The signal sender instance.
    :type instance: boulangerie.apps.projects.models.SSHKey
    :param kwargs: Context.
    :type kwargs: django.db.models.base.ModelBase
    :rtype:None
    """
    payload = {'key': instance.public, 'user': instance.owner}
    boulangerie.broker.send(payload, 'delete-key', 'git')
