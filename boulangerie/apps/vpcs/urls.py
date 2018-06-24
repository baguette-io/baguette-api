#-*- coding:utf-8 -*-
"""
Urls for VPCs.
"""
#pylint:disable=invalid-name
from rest_framework import routers
from .views import VPCsViewSet

router = routers.SimpleRouter()
router.register(r'vpcs/(?P<organization>[^/.]+)', VPCsViewSet, 'VPCs')
urlpatterns = router.urls
