#-*- coding:utf-8 -*-
"""
Urls for Projectss.
"""
#pylint:disable=invalid-name
from rest_framework import routers
from .views import ProjectsViewSet

router = routers.SimpleRouter()
router.register(r'projects/(?P<organization>[^/.]+)', ProjectsViewSet, 'Projects')
urlpatterns = router.urls
