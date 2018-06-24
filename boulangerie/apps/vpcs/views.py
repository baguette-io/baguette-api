"""
Views for the VPCs.
"""
from django.http import Http404
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from dry_rest_permissions.generics import DRYPermissions#pylint:disable=import-error
from boulangerie.apps.organizations.models import Organization
from .serializers import VPCSerializer
from .models import VPC


class VPCsViewSet(viewsets.ModelViewSet):#pylint:disable=too-many-ancestors
    """
    Organizations can create VPCs.
    Organizations can only list/update/delete their VPCs.
    """
    permission_classes = (DRYPermissions,)
    serializer_class = VPCSerializer
    http_method_names = ['get', 'post', 'delete']
    lookup_field = 'name'
    filter_fields = ('name',)

    def get_queryset(self):
        organization = self.kwargs['organization']
        is_member = Organization.objects.has_member(organization, self.request.user.username)
        if is_member:
            return VPC.objects.filter(owner=organization).all()#pylint:disable=no-member
        raise Http404

    def create(self, request, *args, **kwargs):
        """
        Method overrided : We have to add the owner of the VPC.
        """
        if hasattr(request.data, '_mutable'):
            request.data._mutable = True#pylint:disable=protected-access
        request.data['owner'] = kwargs['organization']
        serializer = VPCSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
