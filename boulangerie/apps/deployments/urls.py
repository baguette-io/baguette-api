#-*- coding:utf-8 -*-
"""
Urls for deployments.
"""
#pylint:disable=invalid-name
from rest_framework import routers
from .views import DeploymentsViewSet

router = routers.SimpleRouter()
router.register(r'deployments/(?P<organization>[^/.]+)', DeploymentsViewSet, 'Deployments')
urlpatterns = router.urls
