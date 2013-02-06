from unittest2 import TestCase

from kombu import Connection, Exchange, Queue, Consumer, Producer
from iron_mq import IronMQ
import iron_celery

class test_basic(TestCase):

    def setUp(self):
        self.c = Connection(transport='ironmq')
        self.p = Connection(transport='ironmq')
        self.e = Exchange('test_transport_iron')
        self.q = Queue('test_transport_iron',
                       exchange=self.e,
                       routing_key='test_transport_iron')
        self.q2 = Queue('test_transport_iron2',
                        exchange=self.e,
                        routing_key='test_transport_iron2')
        self.q(self.c.channel()).delete()
        self.q2(self.c.channel()).delete()

    def test_produce_consume_noack(self):
        producer = Producer(self.p.channel(), self.e)
        consumer = Consumer(self.c.channel(), self.q, no_ack=True)

        for i in range(10):
            producer.publish({'foo': i},
                             routing_key='test_transport_iron')

        _received = []

        def callback(message_data, message):
            _received.append(message)

        consumer.register_callback(callback)
        consumer.consume()

        while 1:
            if len(_received) == 10:
                break
            self.c.drain_events()

        self.assertEqual(len(_received), 10)

    def test_produce_consume(self):
        producer_channel = self.p.channel()
        consumer_channel = self.c.channel()
        producer = Producer(producer_channel, self.e)
        consumer1 = Consumer(consumer_channel, self.q)
        consumer2 = Consumer(consumer_channel, self.q2)
        self.q2(consumer_channel).declare()

        for i in range(10):
            producer.publish({'foo': i},
                             routing_key='test_transport_iron')
        for i in range(10):
            producer.publish({'foo': i},
                             routing_key='test_transport_iron2')

        _received1 = []
        _received2 = []

        def callback1(message_data, message):
            _received1.append(message)
            message.ack()

        def callback2(message_data, message):
            _received2.append(message)
            message.ack()

        consumer1.register_callback(callback1)
        consumer2.register_callback(callback2)

        consumer1.consume()
        consumer2.consume()

        while 1:
            if len(_received1) + len(_received2) == 20:
                break
            self.c.drain_events()

        self.assertEqual(len(_received1) + len(_received2), 20)

        # compression
        #producer.publish({'compressed': True},
        #                 routing_key='test_transport_iron',
        #                 compression='zlib')
        #m = self.q(consumer_channel).get()
        #self.assertDictEqual(m.payload, {'compressed': True})

        # queue.delete
        for i in range(10):
            producer.publish({'foo': i},
                             routing_key='test_transport_iron')
        self.assertTrue(self.q(consumer_channel).get())
        self.q(consumer_channel).delete()
        self.q(consumer_channel).declare()
        self.assertIsNone(self.q(consumer_channel).get())

        # queue.purge
        for i in range(10):
            producer.publish({'foo': i},
                             routing_key='test_transport_iron2')
        self.assertTrue(self.q2(consumer_channel).get())
        self.q2(consumer_channel).purge()
        self.assertIsNone(self.q2(consumer_channel).get())
