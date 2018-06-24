#-*- coding:utf-8 -*-
"""
Urls for quotas.
"""
#pylint:disable=invalid-name
from rest_framework import routers
from .views import QuotasViewSet

router = routers.SimpleRouter()
router.register(r'quotas', QuotasViewSet, 'Quotas')
urlpatterns = router.urls
