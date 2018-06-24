"""
Models for the Keys, aka the SSH keys.
"""
from django.db import models
from dry_rest_permissions.generics import authenticated_users #pylint:disable=import-error

class SSHKey(models.Model):
    """
    SSHKey model:
        * name : unique for an account(user/organization), slugified.
        * deletable : always true except for the default one
        * owner : the key owner
    """
    name = models.SlugField(null=False, max_length=50)
    owner = models.SlugField(null=False, max_length=50)
    public = models.TextField()
    fingerprint = models.TextField(max_length=500, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:#pylint:disable=old-style-class,no-init,too-few-public-methods
        """
        We declare the name and the owner as unique, together.
        """
        ordering = ('-date_created',)
        unique_together = (('name', 'owner',))

    #Global permissions:
    @staticmethod
    @authenticated_users
    def has_read_permission(request):#pylint:disable=unused-argument
        """
        Any authenticated user can read(retrieve(), list()) a `SSHKey`.
        """
        return True

    @staticmethod
    @authenticated_users
    def has_write_permission(request):#pylint:disable=unused-argument
        """
        Any authenticated user can write(update(), delete()) a `SSHKey`.
        """
        return True

    @staticmethod
    @authenticated_users
    def has_create_permission(request):#pylint:disable=unused-argument
        """
        Any authenticated user can create if they don't reach their quota
        """
        from boulangerie.apps.quotas.models import Quota
        current = SSHKey.objects.filter(owner=request.user.username).count()
        quota = Quota.objects.get(owner=request.user.username, key='max_keys')
        if current >= quota.value:
            return False
        return True

    #Object permissions:
    def has_object_read_permission(self, request):
        """
        But they can only read theirs SSH keys.
        """
        return self.owner == request.user.username

    def has_object_write_permission(self, request):
        """
        But they can only write theirs SSH keys.
        """
        return self.owner == request.user.username
