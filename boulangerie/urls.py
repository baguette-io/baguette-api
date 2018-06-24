"""
boulangerie urls.
"""
from django.conf.urls import include, url

import boulangerie.views

urlpatterns = [#pylint: disable=invalid-name
    url(r'^api/0.1/accounts/', include('boulangerie.apps.accounts.urls')),
    url(r'^api/0.1/', include('boulangerie.apps.builds.urls')),
    url(r'^api/0.1/', include('boulangerie.apps.deployments.urls')),
    url(r'^api/0.1/', include('boulangerie.apps.keys.urls')),
    url(r'^api/0.1/', include('boulangerie.apps.organizations.urls')),
    url(r'^api/0.1/', include('boulangerie.apps.projects.urls')),
    url(r'^api/0.1/', include('boulangerie.apps.quotas.urls')),
    url(r'^api/0.1/', include('boulangerie.apps.vpcs.urls')),
    url(r'^api/0.1/$', boulangerie.views.dummy)
]
