#-*- coding:utf-8 -*-
"""
Fixtures for the Builds tests.
"""
#pylint:disable=wildcard-import,unused-wildcard-import,line-too-long
import mock
from boulangerie.apps.accounts.tests.fixtures import *

@pytest.fixture
def list_builds():
    """
    Mock the call to the RPC method `build.list()`
    """
    result = {u'count': 2, u'previous': None, u'results': [u'{"tag_uri": null, "context": {}, "uid": "c7c853961d9942ddb0b8619a8ae55408", "repo": "toto", "fail": true, "step": "build-docker", "branch": "master", "owner": "user1-default", "date_created": "2018-01-21T18:08:32.346423", "id": 37}', u'{"tag_uri": "http://registry-docker/user1-default-toto-master", "context": {}, "uid": "3b73f69f3fb94f159d8a3230596c2e3b", "repo": "toto", "fail": false, "step": "done", "branch": "master", "owner": "user1-default", "date_created": "2018-01-21T17:10:59.793568", "id": 28}'], u'next': None}

    with mock.patch("farine.rpc.Client.__wrap_rpc__", mock.Mock(return_value=result)):
        yield

@pytest.fixture
def detail_build():
    """
    Mock the call to the RPC method `build.detail()`
    """
    result = {u'count': 8, u'previous': None, u'results': [u'{"tag_uri": "http://registry-docker/user1-default-toto-master", "context": {}, "uid": "3b73f69f3fb94f159d8a3230596c2e3b", "repo": "toto", "fail": false, "step": "done", "branch": "master", "owner": "user1-default", "date_created": "2018-01-21T17:10:59.793568", "id": 28}', u'{"tag_uri": "http://registry-docker/user1-default-toto-master", "context": {}, "uid": "3b73f69f3fb94f159d8a3230596c2e3b", "repo": "toto", "fail": false, "step": "push-docker", "branch": "master", "owner": "user1-default", "date_created": "2018-01-21T17:10:59.788728", "id": 27}', u'{"tag_uri": null, "context": {}, "uid": "3b73f69f3fb94f159d8a3230596c2e3b", "repo": "toto", "fail": false, "step": "build-docker", "branch": "master", "owner": "user1-default", "date_created": "2018-01-21T17:10:59.782747", "id": 26}', u'{"tag_uri": null, "context": {"domain": "user1-default-toto-master.projects.baguette.io"}, "uid": "3b73f69f3fb94f159d8a3230596c2e3b", "repo": "toto", "fail": false, "step": "generate-dns", "branch": "master", "owner": "user1-default", "date_created": "2018-01-21T17:10:59.774996", "id": 25}', u'{"tag_uri": null, "context": {}, "uid": "3b73f69f3fb94f159d8a3230596c2e3b", "repo": "toto", "fail": false, "step": "generate-dockerfile", "branch": "master", "owner": "user1-default", "date_created": "2018-01-21T17:10:59.772595", "id": 24}', u'{"tag_uri": null, "context": {}, "uid": "3b73f69f3fb94f159d8a3230596c2e3b", "repo": "toto", "fail": false, "step": "generate-definition", "branch": "master", "owner": "user1-default", "date_created": "2018-01-21T17:10:59.767596", "id": 23}', u'{"tag_uri": null, "context": {}, "uid": "3b73f69f3fb94f159d8a3230596c2e3b", "repo": "toto", "fail": false, "step": "generate-recipe", "branch": "master", "owner": "user1-default", "date_created": "2018-01-21T17:10:59.760493", "id": 22}', u'{"tag_uri": null, "context": {"repo": "toto", "branch": "master"}, "uid": "3b73f69f3fb94f159d8a3230596c2e3b", "repo": "toto", "fail": false, "step": "clone", "branch": "master", "owner": "user1-default", "date_created": "2018-01-21T17:10:59.753936", "id": 21}'], u'next': None}
    with mock.patch("farine.rpc.Client.__wrap_rpc__", mock.Mock(return_value=result)):
        yield

@pytest.fixture
def detail_nobuild():
    """
    Mock the call to the RPC method `build.detail()`
    """
    result = {u'count':0, u'previous': None, u'results': []}
    with mock.patch("farine.rpc.Client.__wrap_rpc__", mock.Mock(return_value=result)):
        yield
