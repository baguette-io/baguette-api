#-*- coding:utf-8 -*-
import os
import rabbitpy
import pytest
from pytest_rabbitmq.factories.client import clear_rabbitmq
from django.conf import settings

def pytest_configure():
    current = os.path.abspath(os.path.dirname(__file__))
    os.environ['BOULANGERIE_INI'] = os.path.join(current, 'boulangerie.ini')
    os.environ['FARINE_INI'] = os.path.join(current, 'boulangerie.ini')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'boulangerie.settings'
    import django
    django.setup()


@pytest.fixture(autouse=True)
def farine_ini():
    """
    Load automatically the farine config.
    """
    import farine.settings
    farine.settings.load()

@pytest.fixture
def broker_factory(request, rabbitmq, rabbitmq_proc):
    def factory(exchange_name, name):
        channel = rabbitmq.channel()
        exchange = rabbitpy.Exchange(channel, exchange_name, auto_delete=False, durable=True)
        exchange.declare()
        queue = rabbitpy.Queue(channel, name, auto_delete=False, durable=True)
        queue.declare()
        queue.bind(exchange, routing_key=name)
        return queue, exchange
    def cleanup():
        clear_rabbitmq(rabbitmq_proc, rabbitmq)
    request.addfinalizer(cleanup)
    return factory

@pytest.fixture(autouse=True)
def broker_git_create_key(broker_factory):
    return broker_factory('git', 'create-key')

@pytest.fixture(autouse=True)
def broker_git_delete_key(broker_factory):
    return broker_factory('git', 'delete-key')

@pytest.fixture(autouse=True)
def broker_git_create_member(broker_factory):
    return broker_factory('git', 'create-member')

@pytest.fixture(autouse=True)
def broker_git_delete_member(broker_factory):
    return broker_factory('git', 'delete-member')

@pytest.fixture(autouse=True)
def broker_git_create_repo(broker_factory):
    return broker_factory('git', 'create-repo')

@pytest.fixture(autouse=True)
def broker_git_delete_repo(broker_factory):
    return broker_factory('git', 'delete-repo')

@pytest.fixture(autouse=True)
def broker_git_delete_orga(broker_factory):
    return broker_factory('git', 'delete-organization')

@pytest.fixture(autouse=True)
def broker_namespace_create(broker_factory):
    return broker_factory('namespace', 'create')

@pytest.fixture(autouse=True)
def broker_namespace_delete(broker_factory):
    return broker_factory('namespace', 'delete')
