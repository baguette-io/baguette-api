# -*- coding: utf-8 -*-
"""
Views for the Builds.
"""
import uuid
from django.http import Http404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from boulangerie.apps.organizations.models import Organization


OFFSET = 0
LIMIT = 10

class BuildsViewSet(viewsets.ViewSet):#pylint:disable=too-many-ancestors
    """
    Accounts can only list builds of their organizations.
    """
    permission_classes = [IsAuthenticated]

    def ensure_is_member(self, request, organization):
        """
        Check that the user belongs to the organization.
        :param request: The request's context.
        :type request: object
        :param organization: The organization to retrieve the build(s).
        :type organization: str
        :rtype:bool
        :raises Http404: if the user doesn't belong to the organization.
        """
        if Organization.objects.has_member(organization, request.user.username):
            return True
        raise Http404

    def list(self, request, organization):
        """
        List all the organization builds.
        :param request: The request's context.
        :type request: object
        :param organization: The organization to list the builds.
        :type organization: str
        :rtype:Response
        :raises Http404: if the user doesn't belong to the organization.
        """
        import farine.rpc
        self.ensure_is_member(request, organization)
        offset = int(request.query_params.get('offset', OFFSET))
        limit = int(request.query_params.get('limit', LIMIT))
        return Response(farine.rpc.Client('cuisson').list(organization, offset, limit))

    def retrieve(self, request, organization, pk=None):
        """
        Retrieve a specific organization build.
        :param request: The request's context.
        :type request: object
        :param organization: The organization to retrieve the build.
        :type organization: str
        :rtype:Response
        :raises Http404: if the user doesn't belong to the organization.
        """
        #1. Validate uid
        try:
            uid = uuid.UUID(pk, version=4).hex
        except:
            content = {'uid' : 'not a valid uuid'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        import farine.rpc
        self.ensure_is_member(request, organization)
        return Response(farine.rpc.Client('cuisson').detail(organization, uid))
