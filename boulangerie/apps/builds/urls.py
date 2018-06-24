#-*- coding:utf-8 -*-
"""
Urls for Builds.
"""
#pylint:disable=invalid-name
from rest_framework import routers
from .views import BuildsViewSet

router = routers.SimpleRouter()
router.register(r'builds/(?P<organization>[^/.]+)', BuildsViewSet, 'Builds')
urlpatterns = router.urls
