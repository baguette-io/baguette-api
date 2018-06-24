"""
Models for the quotas.
"""
from django.db import models
from dry_rest_permissions.generics import authenticated_users #pylint:disable=import-error


class Quota(models.Model):
    """
    Quota model:
        * key : Type of the quota (ex: max_projects)
        * value : Quota's threshold.
    """
    key = models.SlugField(null=False, max_length=50)
    value = models.DecimalField(max_digits=15, decimal_places=5)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    owner = models.SlugField()

    class Meta:#pylint:disable=old-style-class,no-init,too-few-public-methods
        """
        We declare the key and the owner as unique, together.
        """
        unique_together = (('key', 'owner',))
        ordering = ('key',)

    #Global permissions:
    @staticmethod
    @authenticated_users
    def has_read_permission(request):#pylint:disable=unused-argument
        """
        Any authenticated user can read(retrieve(), list()) a `Quota`.
        """
        return True

    @staticmethod
    @authenticated_users
    def has_write_permission(request):#pylint:disable=unused-argument
        """
        Nobody can write(create(), update(), delete()) a `Quota`.
        """
        return False

    #Object permissions:
    def has_object_read_permission(self, request):
        """
        But they can only read theirs quotas.
        """
        return True
