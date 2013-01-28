from kombu.transport import TRANSPORT_ALIASES

TRANSPORT_ALIASES["ironmq"] = 'iron_celery.iron_mq_transport:IronMQTransport'
