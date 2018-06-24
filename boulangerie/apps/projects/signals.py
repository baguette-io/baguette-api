#-*- coding:utf-8 -*-
"""
Signal handler for projects.
"""
import boulangerie.broker
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from .models import Project

@receiver(post_save, sender=Project)
def create_repo(sender, instance, **kwargs):#pylint:disable=unused-argument
    """
    When creating a project,
    we need to send a message to our broker.
    :param sender: The signal sender model class.
    :type sender: boulangerie.apps.projects.models.Project
    :param instance: The signal sender instance.
    :type instance: boulangerie.apps.projects.models.Project
    :param kwargs: Context.
    :type kwargs: django.db.models.base.ModelBase
    :rtype:None
    """
    if kwargs.get('created'):
        payload = {'repo':'{0}.{1}'.format(instance.owner, instance.name),
                   'organization':instance.owner}
        boulangerie.broker.send(payload, 'create-repo', 'git')

@receiver(post_delete, sender=Project)
def delete_repo(sender, instance, **kwargs):#pylint:disable=unused-argument
    """
    When deleting a project,
    we need to send a message to our broker.
    :param sender: The signal sender.
    :type sender: boulangerie.apps.projects.models.Project
    :param instance: The signal sender instance.
    :type instance: boulangerie.apps.projects.models.Project
    :param kwargs: Context.
    :type kwargs: django.db.models.base.ModelBase
    :rtype:None
    """
    payload = {'repo':'{0}.{1}'.format(instance.owner, instance.name)}
    boulangerie.broker.send(payload, 'delete-repo', 'git')
