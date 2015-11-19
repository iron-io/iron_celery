import collections
from iron_mq import IronMQ
from kombu.transport.virtual import Channel as BaseChannel
from kombu.transport.virtual import Transport as BaseTransport
from anyjson import loads, dumps
try:
    from queue import Empty
except ImportError:  # Python 2 compatibility
    from Queue import Empty
from kombu.transport.virtual import scheduling
from kombu.utils.encoding import bytes_to_str

IRONMQ_MAX_MESSAGES = 100


class IronMQChannel(BaseChannel):
    _client = None
    _noack_queues = set()
    _extra_consumer_tags = set()
    _default_wait_time_seconds = 30
    _max_message_count = 10
    _iron_mq_timeout = 60

    @property
    def client(self):
        if self._client is None:
            conninfo = self.connection.client
            hostname = conninfo.hostname
            self._queue_message_cache = collections.deque()
            lp_enabled = self.connection.client.transport_options.get('long_polling', True)
            message_count = self.connection.client.transport_options.get('max_message_count', None)
            iron_mq_timeout = self.connection.client.transport_options.get('iron_mq_timeout', None)
            if not lp_enabled:
                self._default_wait_time_seconds = None

            if message_count:
                self._max_message_count = message_count

            if iron_mq_timeout:
                self._iron_mq_timeout = iron_mq_timeout

            self._client = IronMQ(project_id=conninfo.userid, token=conninfo.password,
                                  host=None if hostname == "localhost" else hostname)

        return self._client

    def close(self):
        self._client = None
        super(IronMQChannel, self).close()

    def basic_consume(self, queue, no_ack, *args, **kwargs):
        if no_ack:
            self._noack_queues.add(queue)
            tag = kwargs.get('consumer_tag', None)
            if tag:
                self._extra_consumer_tags.add(tag)

        return super(IronMQChannel, self).basic_consume(queue, no_ack, *args, **kwargs)

    def basic_cancel(self, consumer_tag):
        if consumer_tag in self._consumers:
            queue = self._tag_to_queue[consumer_tag]
            self._noack_queues.discard(queue)

        return super(IronMQChannel, self).basic_cancel(consumer_tag)

    def drain_events(self, timeout=None):
        if not self._consumers or not self.qos.can_consume():
            raise Empty()
        message_cache = self._queue_message_cache

        try:
            return message_cache.popleft()
        except IndexError:
            pass

        res, queue = self._poll(self.cycle, timeout=timeout)
        message_cache.extend((r, queue) for r in res)

        try:
            return message_cache.popleft()
        except IndexError:
            raise Empty()


    def _reset_cycle(self):
        self._cycle = scheduling.FairCycle(
            self._get_bulk, self._active_queues, Empty,
        )


    def _get_bulk(self, queue):
        maxcount = self.qos.can_consume_max_estimate()
        maxcount = self._max_message_count if maxcount is None else max(maxcount, 1)
        if maxcount:
            messages = self._get_from_ironmq(
                queue, count=min(maxcount, IRONMQ_MAX_MESSAGES),
            )
            if messages:
                return self._messages_to_python(messages, queue)
        raise Empty()


    def _get_from_ironmq(self, queue, count=1):
        if 'celery.pidbox' in queue:
            for tag in self._extra_consumer_tags:
                self.basic_cancel(tag)

            return None

        q = self.client.queue(queue)
        try:
            messages = q.reserve(max=count, wait=self._default_wait_time_seconds, timeout=self._iron_mq_timeout)
            return messages
        except:
            return None

    def _message_to_python(self, message, queue_name):
        queue = self.client.queue(queue_name)
        msg_id = message['id']
        payload = loads(bytes_to_str(message['body']))
        if queue_name in self._noack_queues:
            queue.delete(msg_id, message['reservation_id'])
        else:
            payload['properties']['delivery_info'].update(
                {'ironmq_message_id': msg_id, 'ironmq_reservation_id': message['reservation_id'], 'ironmq_queue': queue_name})
        return payload

    def _messages_to_python(self, messages, queue):
        return [self._message_to_python(m, queue) for m in messages['messages']]

    def _put(self, queue_name, message, **kwargs):
        queue = self.client.queue(queue_name)
        queue.post(dumps(message))

    def _get(self, queue_name):
        if 'celery.pidbox' in queue_name:
            for tag in self._extra_consumer_tags:
                self.basic_cancel(tag)

            raise Empty()

        queue = self.client.queue(queue_name)
        try:
            messages = queue.reserve(wait=self._default_wait_time_seconds, timeout=self._iron_mq_timeout)
        except:
            raise Empty()

        if messages is None:
            raise Empty()

        if messages["messages"] is None:
            raise Empty()

        if len(messages["messages"]) == 0:
            raise Empty()

        message = messages["messages"][0]
        parsed_message = loads(message['body'])

        if queue_name in self._noack_queues:
            queue.delete(message['id'], message['reservation_id'])
        else:
            parsed_message['properties']['delivery_info'].update(
                {'ironmq_message_id': message['id'], 'ironmq_reservation_id': message['reservation_id'],
                 'ironmq_queue': queue_name})

        return parsed_message

    def basic_ack(self, delivery_tag):
        delivery_info = self.qos.get(delivery_tag).delivery_info
        queue = self.client.queue(delivery_info['ironmq_queue'])

        try:
            queue.delete(delivery_info['ironmq_message_id'], delivery_info['ironmq_reservation_id'])
        except KeyError:
            pass

        super(IronMQChannel, self).basic_ack(delivery_tag)

    def _purge(self, queue_name):
        try:
            self.client.clearQueue(queue_name)
        except:
            pass

        return 0

    def _size(self, queue_name):
        try:
            details = self.client.getQueueDetails(queue_name)
        except:
            return 0

        return details["size"]


class IronMQTransport(BaseTransport):
    Channel = IronMQChannel

    driver_name = "iron_mq"
    driver_type = "iron_mq"
