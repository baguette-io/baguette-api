"""
Models for the projects, aka apps.
"""
from django.db import models
from dry_rest_permissions.generics import authenticated_users #pylint:disable=import-error
from boulangerie.apps.organizations.models import Organization

class Project(models.Model):
    """
    Project model:
        * name : slugified.
        * uri : URI of the project git.
        * owner: organization
    """
    name = models.SlugField(null=False, max_length=50)
    deletable = models.BooleanField(null=False, default=True)
    uri = models.CharField(blank=False, null=False, max_length=350)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    owner = models.SlugField(null=False, max_length=50)

    class Meta:#pylint:disable=old-style-class,no-init,too-few-public-methods
        """
        We declare the name and the owner as unique, together.
        """
        ordering = ('date_created',)
        unique_together = (('name', 'owner',))

    #Global permissions:
    @staticmethod
    @authenticated_users
    def has_read_permission(request):#pylint:disable=unused-argument
        """
        Any authenticated user can read(retrieve(), list()) a `Project`.
        """
        organization = request.parser_context['kwargs']['organization']
        is_member = Organization.objects.has_member(organization, request.user.username)
        if not is_member:
            return False
        return True

    @staticmethod
    @authenticated_users
    def has_write_permission(request):#pylint:disable=unused-argument
        """
        Any authenticated user can write(update(), delete()) a `Project`.
        """
        return True

    @staticmethod
    @authenticated_users
    def has_create_permission(request):#pylint:disable=unused-argument
        """
        Any authenticated user can create if they don't reach their quota
        """
        from boulangerie.apps.quotas.models import Quota
        organization = request.parser_context['kwargs']['organization']
        is_admin = Organization.objects.has_member(organization, request.user.username, is_admin=True)
        if not is_admin:
            return False
        #
        current = Project.objects.filter(owner=organization).count()
        quota = Quota.objects.get(owner=organization, key='max_projects')
        if current >= quota.value:
            return False
        return True

    #Object permissions:
    def has_object_read_permission(self, request):
        """
        But they can only read theirs Projects.
        """
        return Organization.objects.has_member(self.owner, request.user.username)

    def has_object_write_permission(self, request):
        """
        But they can only write theirs Projects.
        """
        return Organization.objects.has_member(self.owner, request.user.username, is_admin=True)

    def has_object_write_permission(self, request):
        """
        But they can only write theirs VPCS.
        """
        return False

    def has_object_destroy_permission(self, request):
        """
        They can only delete deletable projects.
        """
        return Organization.objects.has_member(self.owner, request.user.username, is_admin=True) and self.deletable
