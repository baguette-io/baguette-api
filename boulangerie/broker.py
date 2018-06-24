#-*- coding:utf-8 -*-
"""
Declare all the queues/exchanges
that the API has to be aware.
And some utils to send message to them.
"""
import kombu
import kombu.common
import kombu.pools
from django.conf import settings

EXCHANGES = {
    'git': kombu.Exchange('git', type='direct'),
    'namespace' : kombu.Exchange('namespace', type='direct'),
    }

def send(payload, routing_key, exchange):
    """
    Send the `payload` to the broker using the `routing_key`.
    :param payload: the data to send.
    :type payload: dict
    :param routing_key: The routing key used to forward the payload.
    :type routing_key: str
    :param exchange: The exchange to send the payload
    :type exchange: str
    :rtype: bool
    """
    exchange = EXCHANGES.get(exchange)
    with kombu.Connection(settings.BROKER['uri']) as conn:
        exchange = exchange(conn.channel())
        exchange.declare()
        with kombu.pools.producers[conn].acquire(block=True) as producer:
            kombu.common.maybe_declare(exchange, producer.channel)
            producer.publish(payload, routing_key=routing_key)
