#-*- coding:utf-8 -*-
"""
Fixtures for the Deployments tests.
"""
#pylint:disable=wildcard-import,unused-wildcard-import,line-too-long
import mock
from boulangerie.apps.accounts.tests.fixtures import *

@pytest.fixture
def list_deployments():
    """
    Mock the call to the RPC method `deployment.list()`
    """
    result = {u'count':2, u'previous': None, u'results': [u'{"uid":"c7c853961d9942ddb0b8619a8ae55408"}', u'{"uid":"3b73f69f3fb94f159d8a3230596c2e3b"}']}
    with mock.patch("farine.rpc.Client.__wrap_rpc__", mock.Mock(return_value=result)):
        yield

@pytest.fixture
def detail_deployment():
    """
    Mock the call to the RPC method `deployment.detail()`
    """
    result = {u'count':8, u'previous': None, u'results': [u'{"uid":"c7c853961d9942ddb0b8619a8ae55408"}', u'{"uid":"c7c853961d9942ddb0b8619a8ae55408"}', u'{"uid":"c7c853961d9942ddb0b8619a8ae55408"}', u'{"uid":"c7c853961d9942ddb0b8619a8ae55408"}', u'{"uid":"c7c853961d9942ddb0b8619a8ae55408"}', u'{"uid":"c7c853961d9942ddb0b8619a8ae55408"}', u'{"uid":"c7c853961d9942ddb0b8619a8ae55408"}', u'{"uid":"c7c853961d9942ddb0b8619a8ae55408"}']}
    with mock.patch("farine.rpc.Client.__wrap_rpc__", mock.Mock(return_value=result)):
        yield

@pytest.fixture
def detail_nodeployment():
    """
    Mock the call to the RPC method `deployment.detail()`
    """
    result = {u'count':0, u'previous': None, u'results': []}
    with mock.patch("farine.rpc.Client.__wrap_rpc__", mock.Mock(return_value=result)):
        yield

@pytest.fixture
def delete_deployment_ok():
    """
    Mock the call to the RPC method `deployment.stop()`
    """
    with mock.patch("farine.rpc.Client.__wrap_rpc__", mock.Mock(return_value=[True])):
        yield

@pytest.fixture
def delete_deployment_nok():
    """
    Mock the call to the RPC method `deployment.stop()`
    """
    with mock.patch("farine.rpc.Client.__wrap_rpc__", mock.Mock(return_value=False)):
        yield
