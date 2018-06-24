#-*- coding:utf-8 -*-
"""
Serializers for the vpcs.
"""

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import VPC

class VPCSerializer(serializers.ModelSerializer):
    """
    VPC serializer:
    * deletable is not writable
    * owner is hidden
    """
    def validate_name(self, value):
        return value.lower()

    class Meta:#pylint:disable=old-style-class,no-init,too-few-public-methods, missing-docstring
        model = VPC
        fields = ('name', 'deletable', 'owner',
                  'date_created', 'date_modified')
        read_only_fields = ('deletable', 'date_created', 'date_modified')
        lookup_field = 'name'
        validators = [
            UniqueTogetherValidator(
                queryset=VPC.objects.all(),#pylint:disable=no-member
                fields=('name', 'owner',),
                message='name must be unique.'
            )
        ]
        extra_kwargs = {
            'owner':{'write_only': True},
        }
