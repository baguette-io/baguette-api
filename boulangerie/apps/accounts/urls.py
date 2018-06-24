#-*- coding:utf-8 -*-
"""
Account urls.
"""
import rest_framework_jwt.views as jwt#pylint:disable=import-error
from django.conf.urls import url
from .views import AccountRegister

urlpatterns = [#pylint: disable=invalid-name
    url(r'^login/', jwt.obtain_jwt_token),
    url(r'^token-refresh/', jwt.refresh_jwt_token),
    url(r'^token-verify/', jwt.verify_jwt_token),
    url(r'^register/$', AccountRegister.as_view()),
]
