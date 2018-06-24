"""
Views for the Quotas.
"""
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from dry_rest_permissions.generics import DRYPermissions#pylint:disable=import-error
from boulangerie.apps.organizations.models import Organization
from .serializers import QuotaSerializer
from .models import Quota

class QuotasViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):#pylint:disable=too-many-ancestors
    """
    Accounts can only list their quotas.
    """
    model = Quota
    permission_classes = (DRYPermissions,)
    serializer_class = QuotaSerializer
    http_method_names = ['get']
    lookup_field = 'key'

    def list(self, request):
        organization = request.query_params.get('organization')
        if not organization:
            queryset = Quota.objects.filter(owner=self.request.user.username).all()
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        #Organization
        is_member = Organization.objects.has_member(organization, self.request.user.username)
        if not is_member:
            return Response(status=status.HTTP_403_FORBIDDEN)
        queryset = Quota.objects.filter(owner=organization).all()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
