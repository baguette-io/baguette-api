#-*- coding:utf-8 -*-
"""
Serializer for the account model.
"""
from rest_framework import serializers
from .models import Account

class AccountSerializer(serializers.ModelSerializer):
    """
    Account Serializer extends from the default ModelSerializer.
    """
    password = serializers.CharField(write_only=True,
                                     required=True,
                                     min_length=6,
                                     error_messages={
                                         "blank": "Password cannot be empty.",
                                         "min_length": "Password too short.",
                                     })
    confirm_password = serializers.CharField(write_only=True, allow_blank=True)

    class Meta:#pylint:disable=old-style-class,missing-docstring,no-init,too-few-public-methods
        model = Account
        fields = (
            'email', 'username', 'date_created', 'date_modified',
            'firstname', 'lastname', 'password', 'confirm_password')
        read_only_fields = ('date_created', 'date_modified')
        extra_kwargs = {
            'account':{'write_only': True},
            'password':{'write_only': True},
        }

    def create(self, validated_data):
        """
    Create an user.
    """
        return Account.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """
    Update the user.
    """
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.firstname = validated_data.get('firstname', instance.firstname)
        instance.lastname = validated_data.get('lastname', instance.lastname)
        instance.company = validated_data.get('company', instance.lastname)

        password = validated_data.get('password', None)
        confirm_password = validated_data.get('confirm_password', None)

        if password and password == confirm_password:
            instance.set_password(password)

        instance.save()
        return instance

    def validate_username(self, value):
        return value.lower()

    def validate(self, data):
        """
        Ensure the passwords are the same.
        """
        if data['password'] and data['password'] != data.get('confirm_password', None):
            raise serializers.ValidationError("The passwords have to be the same")
        return data
