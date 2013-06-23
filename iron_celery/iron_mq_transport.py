from iron_mq import IronMQ
from kombu.transport.virtual import Channel as BaseChannel
from kombu.transport.virtual import Transport as BaseTransport
from anyjson import loads, dumps
from Queue import Empty

class IronMQChannel(BaseChannel):
    _client = None
    _noack_queues = set()

    @property
    def client(self):
        if self._client is None:
            conninfo = self.connection.client
            hostname = conninfo.hostname
            self._client = IronMQ(project_id = conninfo.userid, token = conninfo.password, host = None if hostname == "localhost" else hostname)

        return self._client

    def close(self):
        self._client = None
        super(IronMQChannel, self).close()

    def basic_consume(self, queue, no_ack, *args, **kwargs):
        if no_ack:
            self._noack_queues.add(queue)

        return super(IronMQChannel, self).basic_consume(queue, no_ack, *args, **kwargs)

    def basic_cancel(self, consumer_tag):
        if consumer_tag in self._consumers:
            queue = self._tag_to_queue[consumer_tag]
            self._noack_queues.discard(queue)

        return super(IronMQChannel, self).basic_cancel(consumer_tag)

    def _put(self, queue, message, **kwargs):
        if 'iron_mq_timeout' in message['properties']:
            timeout = message['properties']['iron_mq_timeout']
            self.client.postMessage(queue, [{'body': dumps(message), 'timeout': timeout}])
        else:
            self.client.postMessage(queue, [dumps(message)])

    def _get(self, queue):
        messages = self.client.getMessage(queue)

        if messages is None:
            raise Empty()

        if messages["messages"] is None:
            raise Empty()

        if len(messages["messages"]) == 0:
            raise Empty()

        message = messages["messages"][0]
        parsed_message = loads(message['body'])

        if queue in self._noack_queues:
            self.client.deleteMessage(queue, message['id'])
        else:
            parsed_message['properties']['delivery_info'].update({'ironmq_message_id': message['id'], 'ironmq_queue': queue})

        return parsed_message

    def basic_ack(self, delivery_tag):
        delivery_info = self.qos.get(delivery_tag).delivery_info

        try:
            self.client.deleteMessage(delivery_info['ironmq_queue'], delivery_info['ironmq_message_id'])
        except KeyError:
            pass

        super(IronMQChannel, self).basic_ack(delivery_tag)

    def _purge(self, queue):
        try:
            self.client.clearQueue(queue)
        except:
            pass

        return 0

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
