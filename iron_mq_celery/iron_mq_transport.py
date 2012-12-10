from iron_mq import IronMQ
from kombu.transport.virtual import Channel as BaseChannel
from kombu.transport.virtual import Transport as BaseTransport
from anyjson import loads, dumps
from Queue import Empty

class IronMQChannel(BaseChannel):
    _client = None

    @property
    def client(self):
        if self._client is None:
            self._client = IronMQ()

        return self._client

    def close(self):
        self._client = None
        super(IronMQChannel, self).close()

    def _put(self, queue, message, **kwargs):
        self.client.postMessage(queue, [dumps(message)])

    def _get(self, queue):
        messages = self.client.getMessage(queue)

        if len(messages["messages"]) == 0:
            raise Empty()

        message = messages["messages"][0]

        self.client.deleteMessage(queue, message['id'])

        return loads(message['body'])

    def _purge(self, queue):
        self.client.clearQueue(queue)

    def _size(self, queue):
        try:
            details = self.client.getQueueDetails(queue)
        except:
            return 0

        return details["size"]

class IronMQTransport(BaseTransport):
    Channel = IronMQChannel

    driver_name = "iron_mq"
    driver_type = "iron_mq"
