#-*- coding:utf-8 -*-
"""
Serializers for the keys.
"""
#pylint:disable=line-too-long
import sshpubkeys
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import SSHKey


class SSHKeySerializer(serializers.ModelSerializer):
    """
    SSHKey serializer:
    * fingerprint, owner are hidden
    """

    def validate_public(self, data):
        """
        Validate the public key,
        and generate the fingerprint.
        :param data: The public key to validate.
        :type data: str
        :returns: The validated public key
        :rtype: str
        :raises serializers.ValidationError: If the public key is invalid.
        """
        try:
            ssh = sshpubkeys.SSHKey(data)
            ssh.parse()
        except (sshpubkeys.InvalidKeyException, NotImplementedError):
            self.initial_data['fingerprint'] = 'invalid'
            raise serializers.ValidationError("Invalid key")
        fingerprint = ssh.hash_md5()
        self.initial_data['fingerprint'] = fingerprint
        return data

    def validate_name(self, value):
        return value.lower()

    class Meta:#pylint:disable=old-style-class,no-init,too-few-public-methods, missing-docstring
        model = SSHKey
        fields = ('name', 'public', 'owner', 'fingerprint', 'date_created', 'date_modified')
        read_only_fields = ('date_created', 'date_modified')
        lookup_field = 'name'
        validators = [
            UniqueTogetherValidator(
                queryset=SSHKey.objects.all(),#pylint:disable=no-member
                fields=('name', 'owner'),
                message='name must be unique.'
            )
        ]
        extra_kwargs = {
            'owner':{'write_only': True},
        }
