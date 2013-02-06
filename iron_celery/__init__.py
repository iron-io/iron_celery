from kombu.transport import TRANSPORT_ALIASES
from celery.backends import BACKEND_ALIASES

TRANSPORT_ALIASES["ironmq"] = 'iron_celery.iron_mq_transport:IronMQTransport'
BACKEND_ALIASES["ironcache"] = 'iron_celery.iron_cache_backend:IronCacheBackend'
