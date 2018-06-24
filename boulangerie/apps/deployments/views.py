# -*- coding: utf-8 -*-
"""
Views for the Deployments.
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

class DeploymentsViewSet(viewsets.ViewSet):#pylint:disable=too-many-ancestors
    """
    Accounts can only list deployments of their organizations.
    """
    permission_classes = [IsAuthenticated]

    def ensure_is_member(self, request, organization):
        """
        Check that the user belongs to the organization.
        :param request: The request's context.
        :type request: object
        :param organization: The organization to retrieve the deployment(s).
        :type organization: str
        :rtype:bool
        :raises Http404: if the user doesn't belong to the organization.
        """
        if Organization.objects.has_member(organization, request.user.username):
            return True
        raise Http404

    def list(self, request, organization):
        """
        List all the organization deployments.
        :param request: The request's context.
        :type request: object
        :param organization: The organization to list the deployments.
        :type organization: str
        :rtype:Response
        :raises Http404: if the user doesn't belong to the organization.
        """
        self.ensure_is_member(request, organization)
        offset = int(request.query_params.get('offset', OFFSET))
        limit = int(request.query_params.get('limit', LIMIT))
        import farine.rpc
        return Response(farine.rpc.Client('defournement').list(organization, offset, limit))

    def retrieve(self, request, organization, pk=None):
        """
        Retrieve a specific organization deployment.
        :param request: The request's context.
        :type request: object
        :param organization: The organization to retrieve the deployment.
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
        self.ensure_is_member(request, organization)
        import farine.rpc
        return Response(farine.rpc.Client('defournement').detail(organization, uid))

    def destroy(self, request, organization, pk=None):
        """
        Stop a specific organization deployment.
        :param request: The request's context.
        :type request: object
        :param organization: The organization to stop the deployment.
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
        self.ensure_is_member(request, organization)
        import farine.rpc
        result = farine.rpc.Client('defournement').delete(organization, uid)
        if not result:
            return Response({'error':'error while destroying the deployment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_204_NO_CONTENT)
