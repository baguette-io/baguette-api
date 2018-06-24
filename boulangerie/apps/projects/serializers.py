#-*- coding:utf-8 -*-
"""
Serializers for the projects.
"""
from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """
    Project serializer:
    * uri is not writable
    * owner is hidden
    """
    def validate_name(self, value):
        return value.lower()

    def validate(self, data):
        """
        Add the URI of the project.
        """
        data['uri'] = settings.URI_TEMPLATE.format(data['owner'],
                                                   data['name'])#pylint:disable=no-member
        return data

    class Meta:#pylint:disable=old-style-class,no-init,too-few-public-methods, missing-docstring
        model = Project
        fields = ('name', 'uri', 'owner', 'date_created', 'date_modified', 'deletable')
        read_only_fields = ('uri', 'date_created', 'date_modified')
        lookup_field = 'name'
        validators = [
            UniqueTogetherValidator(
                queryset=Project.objects.all(),#pylint:disable=no-member
                fields=('name', 'owner'),
                message='name must be unique.'
            )
        ]
        extra_kwargs = {
            'owner':{'write_only': True},
        }
