# -*- coding: utf-8 -*-
"""
Organization modelisation.
Pretty naive.
"""
from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType
from dry_rest_permissions.generics import authenticated_users #pylint:disable=import-error


class OrganizationManager(models.Manager):
    """
    Manager for organization.
    """

    def by_member(self, account, is_admin=None, is_owner=None):
        """
        Retrieve the organizations that an account belongs to.
        """
        if is_owner is not None:
            accounts = Member.objects.filter(account=account, is_owner=is_owner).values('organization')
        elif is_admin is not None:
            accounts = Member.objects.filter(account=account, is_admin=is_admin).values('organization')
        else:
            accounts = Member.objects.filter(account=account).values('organization')
        return self.get_queryset().filter(name__in=accounts)

    def has_member(self, organization, account, is_admin=None, is_owner=None):
        """
        Check if the account is in the organization.
        """
        if not organization or not account:
            return False
        if is_owner is not None:
            exist = Member.objects.filter(account=account, organization=organization, is_owner=is_owner).first()
        elif is_admin is not None:
            exist = Member.objects.filter(account=account, organization=organization, is_admin=is_admin).first()
        else:
            exist = Member.objects.filter(account=account, organization=organization).first()
        return bool(exist)

class Organization(models.Model):
    """
    Organization is just a name and a description.
    among organizations and users.
    """
    name = models.SlugField(null=False, max_length=50, primary_key=True)
    description = models.SlugField(null=True, blank=True, max_length=50)
    deletable = models.BooleanField(null=False, default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    objects = OrganizationManager()

    class Meta:#pylint:disable=old-style-class,no-init,too-few-public-methods
        """
        Sorted by date_created
        """
        ordering = ('-date_created',)

    def has_member(self, account, is_owner=None):
        """
        Check if the account is in the organization.
        """
        if is_owner is not None:
            exist = Member.objects.filter(account=account, organization=self.name, is_owner=is_owner).first()
        else:
            exist = Member.objects.filter(account=account, organization=self.name).first()
        return bool(exist)

    def stats(self):
        """
        Retrieve some statictics:
          - number of members.
          - number of invitations.
        """
        members = Member.objects.filter(organization=self.name).count()
        invits = Invitation.objects.filter(organization=self.name).count()
        return {'members': members, 'invitations': invits}

    #Global permissions:
    @staticmethod
    @authenticated_users
    def has_read_permission(request):#pylint:disable=unused-argument
        """
        Any user can read(retrieve(), list()) an organization.
        """
        return True

    @staticmethod
    @authenticated_users
    def has_write_permission(request):#pylint:disable=unused-argument
        """
        Any user can write(update(), delete()) an organization.
        """
        return True

    @staticmethod
    @authenticated_users
    def has_create_permission(request):#pylint:disable=unused-argument
        """
        Any authenticated user can create if they don't reach their quota.
        """
        from boulangerie.apps.quotas.models import Quota
        owner_type = ContentType.objects.get(app_label='accounts', model='account')
        current = Organization.objects.by_member(request.user.username, is_owner=True).count()
        quota = Quota.objects.get(owner=request.user.username, key='max_organizations')
        if current >= quota.value:
            return False
        return True

    #Object permissions:
    def has_object_read_permission(self, request):
        """
        But they can only read the organizations they are members.
        """
        return self.has_member(request.user.username)

    def has_object_write_permission(self, request):
        """
        But they can only write the organizations they are owners.
        """
        return self.has_member(request.user.username, is_owner=True)

class Member(models.Model):
    """
    A member of an organization can be admin or member:
    no permission management for the moment.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    account = models.SlugField(null=False, max_length=50)
    is_admin = models.BooleanField(null=False, default=False)
    is_owner = models.BooleanField(null=False, default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:#pylint:disable=old-style-class,no-init,too-few-public-methods
        """
        We declare the organization and the account as unique, together.
        """
        unique_together = (('organization', 'account',))
        ordering = ('-date_created',)

    #Global permissions:
    @staticmethod
    @authenticated_users
    def has_read_permission(request):#pylint:disable=unused-argument
        """
        Any user can read(retrieve(), list()) members.
        """
        return True

    @staticmethod
    @authenticated_users
    def has_write_permission(request):#pylint:disable=unused-argument
        """
        Any user can write(update(), delete()) a member
        """
        return True

    @staticmethod
    @authenticated_users
    def has_create_permission(request):#pylint:disable=unused-argument
        """
        Nobody can create member
        """
        return False

    #Object permissions:
    def has_object_read_permission(self, request):
        """
        But they can only read members from their organizations.
        """
        return self.organization.has_member(request.user.username)

    def has_object_write_permission(self, request):
        """
        But they can only update a member if they are admin.
        """
        return self.organization.has_member(request.user.username, is_admin=True)

    def has_object_destroy_permission(self, request):
        """
        But they can only delete a member if they are admin/owner.
        """
        return self.organization.has_member(request.user.username, is_admin=True)

class Invitation(models.Model):
    """
    An organization can invite any user.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    account = models.SlugField(null=False, max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:#pylint:disable=old-style-class,no-init,too-few-public-methods
        """
        We declare the organization and the account as unique, together.
        """
        unique_together = (('organization', 'account',))
        ordering = ('-date_created',)

    #Global permissions:
    @staticmethod
    @authenticated_users
    def has_read_permission(request):#pylint:disable=unused-argument
        """
        Any user can read(retrieve(), list()) an invitation.
        """
        return True

    @staticmethod
    @authenticated_users
    def has_write_permission(request):#pylint:disable=unused-argument
        """
        Any user can write(update(), delete()) an invitation.
        """
        return True

    @staticmethod
    @authenticated_users
    def has_create_permission(request):#pylint:disable=unused-argument
        """
        Any authenticated user  that has an organization can create if they don't reach their quota
        """
        return True

    #Object permissions:
    def has_object_read_permission(self, request):
        """
        But they can only read theirs invitations.
        """
        return self.account == request.user.username

    def has_object_write_permission(self, request):
        """
        But they can only accept/refuse theirs invitations.
        """
        return self.account == request.user.username

    def has_object_destroy_permission(self, request):
        """
        But they can only accept/refuse theirs invitations.
        """
        return self.account == request.user.username or bool(Organization.objects.has_member(request.user.username, admin=True).first())
