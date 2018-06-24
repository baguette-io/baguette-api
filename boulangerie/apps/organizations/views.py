# -*- coding: utf-8 -*-
"""
Views for the organizations.
"""
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from dry_rest_permissions.generics import DRYPermissions#pylint:disable=import-error
from .serializers import InvitationSerializer, MemberSerializer, OrganizationSerializer
from .models import Invitation, Organization, Member
from boulangerie.apps.accounts.models import Account


class OrganizationsViewSet(viewsets.ModelViewSet):#pylint:disable=too-many-ancestors
    """
    Accounts can create Organizations.
    Accounts can only list their organizations.
    Owner can only delete organizations.
    """
    permission_classes = (DRYPermissions,)
    serializer_class = OrganizationSerializer
    http_method_names = ['get', 'post', 'delete']
    lookup_field = 'name'
    filter_fields = ('name',)

    def get_queryset(self):
        return Organization.objects.by_member(self.request.user.username).all()

    def destroy(self, request, name=None):
        """
        Override the destroy method, as we can delete an organization only if we are owner.
        """
        member = Member.objects.filter(organization=name, account=request.user.username).first()
        if not member:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not member.is_owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        organization = Organization.objects.get(name=name)
        if not organization.deletable:
            return Response(status=status.HTTP_403_FORBIDDEN)
        organization.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class InvitationsViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):#pylint:disable=too-many-ancestors
    """
    Admin can create invitations.
    Accounts can only accept/reject invitations.
    """
    permission_classes = (DRYPermissions,)
    serializer_class = InvitationSerializer
    http_method_names = ['get', 'post', 'put', 'delete']
    lookup_field = 'organization'
    filter_fields = ('organization', 'account')

    def get_queryset(self):
        return Invitation.objects.filter(account=self.request.user.username).all()

    def retrieve(self, request, *args, **kwargs):
        """
        Override the GET detail method (aka : /invitations/<organization>/):
        we must list the organization invitations.
        """
        is_member = Organization.objects.has_member(kwargs.get('organization'), request.user.username)
        if not is_member:
            return Response(status=status.HTTP_404_NOT_FOUND)
        queryset = Invitation.objects.filter(organization=kwargs.get('organization'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = InvitationSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['delete'], url_path='(?P<account>.+)', permission_classes=(DRYPermissions,))
    def delete(self, request, organization=None, account=None):
        """
        Override the destroy method, as we can delete an invitation if we are admin or the invited one.
        """
        #Check if the client is admin of the organization or invited.
        is_admin = Organization.objects.has_member(organization, request.user.username, is_admin=True)
        invitation = Invitation.objects.filter(organization=organization, account=account).first()
        if invitation and (is_admin or account == request.user.username):
            invitation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        """
        Method overrided : When we do a PUT, we accept the invitation.
        """
        organization = Organization.objects.filter(name=kwargs.get('organization')).first()
        if not organization:
            return Response(status=status.HTTP_404_NOT_FOUND)
        account = request.user.username
        invitation = Invitation.objects.filter(organization=organization, account=account).first()
        if not invitation:
            return Response(status=status.HTTP_404_NOT_FOUND)
        invitation.delete()
        Member.objects.create(organization=organization, account=account)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        """
        Method overrided : We have to check that the organization belongs to the account that requests.
        """
        serializer = InvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #1. Check that the organization and the account exists.
        orga = Organization.objects.has_member(self.request.data.get('organization'), self.request.user.username, is_admin=True)
        account = Account.objects.filter(username=self.request.data.get('account')).first()
        if not orga or not account:
            return Response(serializer.data, status=status.HTTP_404_NOT_FOUND)
        #2. Check that the account is not already a member of the organization
        is_member = Organization.objects.has_member(self.request.data['organization'], self.request.data['account'])
        if is_member:
            return Response(serializer.data, status=status.HTTP_409_CONFLICT)
        #3. Create
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MembersViewSet(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):#pylint:disable=too-many-ancestors
    """
    Admin can update members permissions, and delete them.
    Member can only list the members.
    """
    permission_classes = (DRYPermissions,)
    serializer_class = MemberSerializer
    http_method_names = ['get', 'patch', 'delete']
    lookup_field = 'organization'
    filter_fields = ('organization', 'account')
    def get_queryset(self):
        return Member.objects.filter(account=self.request.user.username).all()


    def retrieve(self, request, *args, **kwargs):
        """
        Override the GET detail method (aka : /members/<organization>/):
        we must list the organization members.
        """
        is_member = Organization.objects.has_member(kwargs.get('organization'), request.user.username)
        if not is_member:
            return Response(status=status.HTTP_403_FORBIDDEN)
        queryset = Member.objects.filter(organization=kwargs.get('organization'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = InvitationSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['delete'], url_path='(?P<account>.+)', permission_classes=(DRYPermissions,))
    def delete(self, request, organization=None, account=None):
        """
        Override the destroy method, as we can delete a member if we are admin.
        """
        #Check if the client is admin of the organization or invited.
        member = Member.objects.filter(organization=organization, account=request.user.username).first()
        target = Member.objects.filter(organization=organization, account=account).first()
        #1. Member check
        if not member:
            return Response(status=status.HTTP_404_NOT_FOUND)
        #2. target check (cannot remove the owner)
        if target.is_owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        #3. If we try to remove ourselves
        if member == target:
            target.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        #4. If we try to remove someone else but we are not admin
        if not member.is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)
        target.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, organization=None):
        """
        Method overrided : When we do a PATCH, we update the member permissions.
        """
        account = request.data.get('account')
        member = Member.objects.filter(organization=organization, account=request.user.username).first()
        exist = Member.objects.filter(organization=organization, account=account).first()
        if not member or not exist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif not member.is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)
        elif exist.is_owner:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = MemberSerializer(exist, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
