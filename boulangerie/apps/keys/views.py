"""
Views for the Keys.
"""
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from dry_rest_permissions.generics import DRYPermissions#pylint:disable=import-error
from .serializers import SSHKeySerializer
from .models import SSHKey


class SSHKeysViewSet(viewsets.ModelViewSet):#pylint:disable=too-many-ancestors
    """
    Accounts can create SSH keys.
    Accounts can only list/update/delete their SSH keys.
    """
    permission_classes = (DRYPermissions,)
    serializer_class = SSHKeySerializer
    http_method_names = ['get', 'post', 'delete']
    lookup_field = 'name'

    def get_queryset(self):
        return SSHKey.objects.filter(owner=self.request.user.username).all()#pylint:disable=no-member

    def create(self, request, *args, **kwargs):
        """
        Method overrided : We have to add the owner of the SSH key and the fingerprint.
        """
        if hasattr(request.data, '_mutable'):
            request.data._mutable = True#pylint:disable=protected-access
        request.data['owner'] = request.user.username
        serializer = SSHKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
