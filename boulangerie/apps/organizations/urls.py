#-*- coding:utf-8 -*-
"""
Urls for Organizations.
"""
#pylint:disable=invalid-name
from rest_framework import routers
from .views import InvitationsViewSet, MembersViewSet, OrganizationsViewSet

router = routers.SimpleRouter()
router.register(r'organizations', OrganizationsViewSet, 'Organizations')
router.register(r'invitations', InvitationsViewSet, 'Invitations')
router.register(r'members', MembersViewSet, 'Members')
urlpatterns = router.urls
