import json
import logging
import pika
from pika.adapters.tornado_connection import TornadoConnection
from tornado.concurrent import run_on_executor

from herald.herald_server.utils import tp_executor

LOG = logging.getLogger(__name__)


RECONNECT_DELAY = 5
RECONNECT_ATTEMPTS = 100

DEAD_LETTER_DELAY = 5000


class Consumer:
    """
    RabbitMQ consumer with automatic reconnects.
    Uses Default Exchange.
    """

    def __init__(self, queue, host, port, user, password):
        self.queue = queue
        self.dlx_exchange = 'dlx'
        self.consume_callback = None
        self.executor = tp_executor

        credentials = pika.PlainCredentials(user, password)
        self.connection_parameters = pika.ConnectionParameters(
            host=host,
            port=int(port),
            credentials=credentials,
            connection_attempts=RECONNECT_ATTEMPTS,
            retry_delay=RECONNECT_DELAY
        )

        self._connection = None
        self._channel = None

    @property
    def delayed_queue(self):
        return self.queue + '_delayed'

    def connect(self):
        LOG.info('Connecting to rabbit')

        self._connection = TornadoConnection(
            self.connection_parameters,
            self.on_connection_open,
            self.on_connection_error
        )

    def on_connection_error(self, _connection, _exception):
        LOG.error('Failed to connect to rabbitmq. Will try to reconnect')
        self._connection.ioloop.add_timeout(5, self.connect)

    def on_connection_open(self, _connection):
        LOG.info('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        LOG.info('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code):
        self._channel = None
        LOG.warning('Connection closed, reopening in 5 seconds: (%s)',
                    reply_code)
        self._connection.ioloop.add_timeout(5, self.connect)

    def open_channel(self):
        LOG.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        LOG.info('Channel opened')
        self._channel = channel
        self.setup_dlx_exchange()

    def setup_dlx_exchange(self):
        LOG.info('Declaring exchange %s', self.dlx_exchange)
        self._channel.exchange_declare(self.dlx_exchange,
                                       callback=self.on_dlx_exchange_declareok)

    def on_dlx_exchange_declareok(self, unused_frame):
        LOG.info('Exchange declared')
        self.setup_queue()

    def setup_queue(self):
        LOG.info('Declaring queue %s', self.queue)
        self._channel.queue_declare(self.queue,
                                    callback=self.on_queue_declareok,
                                    durable=True)

    def on_queue_declareok(self, unused_frame):
        LOG.info('Queue declared successfully')
        self._channel.queue_bind(self.queue,
                                 exchange=self.dlx_exchange,
                                 callback=self.on_queue_bind_ok)

    def on_queue_bind_ok(self, unused_frame):
        self.setup_delayed_queue()

    def setup_delayed_queue(self):
        LOG.info('Declaring delayed queue %s', self.delayed_queue)
        self._channel.queue_declare(self.delayed_queue,
                                    callback=self.on_delayed_queue_declareok,
                                    durable=True,
                                    arguments={
                                        'x-message-ttl': DEAD_LETTER_DELAY,
                                        'x-dead-letter-exchange': self.dlx_exchange,
                                        'x-dead-letter-routing-key': self.queue
                                    })

    def on_delayed_queue_declareok(self, unused_frame):
        LOG.info('Delayed queue declared successfully')
        self.start_consuming()

    def start_consuming(self):
        LOG.info('Starting consuming')
        self._consumer_tag = self._channel.basic_consume(self.queue, self.on_message)

    @run_on_executor
    def on_message(self, unused_channel, basic_deliver, properties, body, callback=None):
        def ack_this_message():
            self.acknowledge_message(basic_deliver.delivery_tag)

        self.consume_callback(body, ack_this_message)
        if callback:
            callback(None)

    def acknowledge_message(self, delivery_tag):
        self._channel.basic_ack(delivery_tag)

    def run(self, consume_callback):
        LOG.info('Launching consumer')
        self.consume_callback = consume_callback
        self.connect()
        self._connection.ioloop.start()

    def _publish_message(self, message, queue):
        if self._channel is None:
            # connection not available
            LOG.error(
                'Failed to publish message. Rabbit connection not available')
            return

        self._channel.basic_publish(
            '', queue, json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2))

    def publish_message(self, message):
        self._publish_message(message, self.queue)

    def publish_delayed_message(self, message):
        self._publish_message(message, self.delayed_queue)
