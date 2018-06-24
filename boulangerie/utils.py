#-*- coding:utf-8 -*-
"""
Collections of utils for boulangerie.
"""
from functools import wraps
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

def skip_signal():
    """
    Skip signal sent.
    """
    def _skip_signal(signal_func):
        @wraps(signal_func)
        def _decorator(sender, instance, **kwargs):
            if hasattr(instance, 'skip_signal'):
                return None
            return signal_func(sender, instance, **kwargs)
        return _decorator
    return _skip_signal

class GenericFKSerializer(serializers.SlugRelatedField):
    """
    Serializer for foreign keys wich depend also on the owner generic field.
    """

    def __init__(self, app_label, model_name, **kwargs):
        """
        Takes two required parameters.
        :param app_label: App label of the model foreign key.
        :type app_label: str
        :param model_name: Model name of the foreign key.
        :type model_name: str
        :rtype: None
        """
        super(GenericFKSerializer, self).__init__(**kwargs)
        self.model = apps.get_model(app_label=app_label, model_name=model_name)
        #kwargs['default'] = self.hop.get(name=kwargs['default'])

    def get_queryset(self):
        """
        Build the query using contenttype.
        """
        owner_type = ContentType.objects.get(app_label='accounts', model='account')
        owner_id = self.context['request'].user.id
        return self.model.objects.filter(owner_type=owner_type, owner_id=owner_id).all()#pylint:disable=no-member

    def get_default(self):
        """
        Build the default value using contenttype.
        """
        owner_type = ContentType.objects.get(app_label='accounts', model='account')
        owner_id = self.context['request'].user.id
        return self.model.objects.get(owner_type=owner_type, owner_id=owner_id, name=self.default)#pylint:disable=no-member
