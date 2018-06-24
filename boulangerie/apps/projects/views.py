"""
Views for the Projects.
"""
from django.http import Http404
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from dry_rest_permissions.generics import DRYPermissions#pylint:disable=import-error
from boulangerie.apps.organizations.models import Organization
from .serializers import ProjectSerializer
from .models import Project


class ProjectsViewSet(viewsets.ModelViewSet):#pylint:disable=too-many-ancestors
    """
    Accounts can create Projects.
    Accounts can only list/update/delete their Projects.
    """
    permission_classes = (DRYPermissions,)
    serializer_class = ProjectSerializer
    http_method_names = ['get', 'post', 'delete']
    lookup_field = 'name'

    def get_queryset(self):
        organization = self.kwargs['organization']
        is_member = Organization.objects.has_member(organization, self.request.user.username)
        if is_member:
            return Project.objects.filter(owner=organization).all()#pylint:disable=no-member
        raise Http404

    def create(self, request, *args, **kwargs):
        """
        Method overrided : We have to add the owner of the Project.
        """
        if hasattr(request.data, '_mutable'):
            request.data._mutable = True#pylint:disable=protected-access
        request.data['owner'] = kwargs['organization']
        serializer = ProjectSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
