#-*- coding:utf-8 -*-
"""
Signal handler for keys.
"""
import boulangerie.broker
from django.dispatch import receiver
from django.db.models.signals import post_delete
from .models import Account

@receiver(post_delete, sender=Account)
def delete_user(sender, instance, **kwargs):#pylint:disable=unused-argument
    """
    When deleting an user,
    we need to send a message to our broker.
    :param sender: The signal sender.
    :type sender: boulangerie.apps.projects.models.SSHKey
    :param instance: The signal sender instance.
    :type instance: boulangerie.apps.projects.models.SSHKey
    :param kwargs: Context.
    :type kwargs: django.db.models.base.ModelBase
    :rtype:None
    """
    payload = {'user': instance.username}
    boulangerie.broker.send(payload, 'delete-user', 'git')
