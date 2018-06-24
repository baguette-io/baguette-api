#-*- coding:utf-8 -*-
"""
User models.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager

class AccountManager(BaseUserManager):
    """
    Manager for our Account model.
    Can create quickly user with it.
    """
    def create_user(self, email, password=None, **kwargs):
        """
        Create an user.
        :param email: The user email, required.
        :type email: str
        :param password: The user password, optional(will be generated).
        :type password: None, str
        :param kwargs: Optional parameters (cf `Account`).
        :type kwargs: dict
        :rtype: None
        """
        # Ensure that an email address is set
        if not email:
            raise ValueError('Users must have a valid e-mail address')

        # Ensure that a username is set
        if not kwargs.get('username'):
            raise ValueError('Users must have a valid username')

        account = self.model(
            email=self.normalize_email(email),
            username=kwargs.get('username'),
            firstname=kwargs.get('firstname', None),
            lastname=kwargs.get('lastname', None),
            company=kwargs.get('company', None),
        )

        account.set_password(password)
        account.save()
        return account

    def create_superuser(self, email, password=None, **kwargs):
        """
        Create an admin account.
        """
        account = self.create_user(email, password, **kwargs)
        account.is_admin = True
        account.save()
        return account

class Account(AbstractBaseUser, PermissionsMixin):#pylint: disable=abstract-method
    """
    Account model. Inherit of the AbstractBaseUser.
    """
    username = models.SlugField(unique=True, max_length=50, db_index=True, primary_key=True)#TODO:check that it's always lower case
    email = models.EmailField(unique=True)

    firstname = models.CharField(max_length=100, null=True)
    lastname = models.CharField(max_length=100, null=True)
    company = models.CharField(max_length=100, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    is_admin = models.BooleanField(default=False)

    objects = AccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']#USERNAME_FIELD must not be on REQUIRED_FIELDS

    @property
    def is_superuser(self):
        """
        AbstractBaseUser requirement.
        """
        return self.is_admin

    @property
    def is_staff(self):
        """
        AbstractBaseUser requirement.
        """
        return self.is_admin

    def get_short_name(self):
        return self.firstname or self.username
