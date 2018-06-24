#-*- coding:utf-8 -*-
"""
Serializers for the quotas.
"""

from rest_framework import serializers
from .models import Quota


class QuotaSerializer(serializers.ModelSerializer):
    """
    Quota serializer:
    * owner is hidden
    """
    class Meta:#pylint:disable=old-style-class,no-init,too-few-public-methods, missing-docstring
        model = Quota
        fields = ('key', 'value', 'owner',
                  'date_created', 'date_modified')
        lookup_field = 'key'
        extra_kwargs = {
            'owner':{'write_only': True},
        }
