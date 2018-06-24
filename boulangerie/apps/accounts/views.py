#-*- coding:utf-8 -*-
"""
Account views.
"""
import sshpubkeys
from Crypto.PublicKey import RSA
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from boulangerie.apps.keys.models import SSHKey
from .models import Account
from .serializers import AccountSerializer

class AccountRegister(APIView):
    """
    Register a new user.
    """
    serializer_class = AccountSerializer
    permission_classes = (AllowAny,)

    def post(self, request, **kwargs):#pylint:disable=all
        if hasattr(request.data, '_mutable'):
            request.data._mutable = True#pylint:disable=protected-access
        #1. Create the account
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        #2. Create it's SSH key
        account = Account.objects.get(username=serializer.data['username'],
                                      email=serializer.data['email'])
        key = RSA.generate(4096)
        model = SSHKey(
            name='default',
            owner=account.username,
            public=key.exportKey('OpenSSH'),
            fingerprint=sshpubkeys.SSHKey(key.exportKey('OpenSSH')).hash_md5()
        )
        model.user_creation = True
        model.organization_creation = True
        model.save()
        key = {
            'name': model.name,
            'private': key.exportKey('PEM'),
            'public': model.public,
            'fingerprint': model.fingerprint
        }
        return Response({'account':serializer.data, 'key': key}, status=status.HTTP_201_CREATED)
