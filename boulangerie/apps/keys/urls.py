#-*- coding:utf-8 -*-
"""
Urls for keys.
"""
#pylint:disable=invalid-name
from rest_framework import routers
from .views import SSHKeysViewSet

router = routers.SimpleRouter()
router.register(r'keys', SSHKeysViewSet, 'Keys')
urlpatterns = router.urls
