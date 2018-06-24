from django.utils.text import slugify#-*- coding:utf-8 -*-
"""
Serializers for the organizations.
"""
#pylint:disable=line-too-long
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from boulangerie.apps.accounts.models import Account
from .models import Invitation, Member, Organization


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Organization serializer:
    * name
    * description
    * deletable
    * stats
    """
    stats = serializers.DictField(required=False)

    class Meta:#pylint:disable=old-style-class,no-init,too-few-public-methods, missing-docstring
        model = Organization
        fields = ('name', 'description', 'deletable', 'date_created', 'date_modified', 'stats')
        read_only_fields = ('date_created', 'date_modified', 'stats', )
        lookup_field = 'name'
        depth = 1

    def validate_description(self, value):
        if value:
            return value.lower()
        return value

    def validate_name(self, value):
        """
        Name must be unique among organization and accounts.
        """
        value = value.lower()
        exist_orga = Organization.objects.filter(name=value).first()
        exist_user = Account.objects.filter(username=value).first()
        if exist_orga or exist_user:
            raise serializers.ValidationError("name must be unique")
        return value

    def create(self, validated_data):
        orga = Organization.objects.create(**validated_data)
        account = self.context['request'].user.username
        Member.objects.create(account=account, organization=orga, is_owner=True, is_admin=True)
        return orga

class MemberSerializer(serializers.ModelSerializer):
    """
    Member serializer:
    * organization, account, date_created, date_modified, is_admin, is_owner
    """
    organization = OrganizationSerializer()

    class Meta:#pylint:disable=old-style-class,no-init,too-few-public-methods, missing-docstring
        model = Member
        fields = ('account', 'is_owner', 'is_admin', 'date_created', 'date_modified', 'organization')
        read_only_fields = ('is_owner', 'date_created', 'date_modified', 'organization')
        depth = 1

class InvitationSerializer(serializers.ModelSerializer):
    """
    Invitation serializer:
    * organization, account, date_created, date_modified
    """
    class Meta:#pylint:disable=old-style-class,no-init,too-few-public-methods, missing-docstring
        model = Invitation
        fields = ('account', 'organization', 'date_created',)
        read_only_fields = ('date_created',)
        lookup_field = 'organization'
        validators = [
            UniqueTogetherValidator(
                queryset=Invitation.objects.all(),#pylint:disable=no-member
                fields=('organization', 'account', ),
                message='invitation must be unique.'
            )
        ]

    def to_representation(self, instance):
       ret = super(InvitationSerializer, self).to_representation(instance)
       orga = instance.organization if isinstance(instance, Invitation) else instance['organization'] 
       ret['organization'] = OrganizationSerializer(orga).data
       return ret
