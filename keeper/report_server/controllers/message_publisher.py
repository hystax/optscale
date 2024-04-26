import json
import logging
import pika
from pika.adapters.tornado_connection import TornadoConnection


LOG = logging.getLogger(__name__)

RECONNECT_DELAY = 2
RECONNECT_ATTEMPTS = 100


class Publisher:
    """
    RabbitMQ publisher with automatic reconnects.
    Uses TornadoConnection to reuse tornado IOLoop for async tasks.
    Uses Default Exchange.
    """

    def __init__(self, queue, host, port, user, password):
        self.queue = queue

        credentials = pika.PlainCredentials(user, password)
        self.connection_parameters = pika.ConnectionParameters(
            host=host,
            port=int(port),
            credentials=credentials,
            connection_attempts=RECONNECT_ATTEMPTS,
            retry_delay=RECONNECT_DELAY,
        )

        self._connection = None
        self._channel = None

    def connect(self):
        LOG.info("Connecting to rabbit")

        self._connection = TornadoConnection(
            self.connection_parameters, self.on_connection_open
        )

    def on_connection_open(self, unused_connection):
        LOG.info("Connection opened")
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        LOG.info("Adding connection close callback")
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        LOG.warning(
            "Connection closed, reopening in 5 seconds: (%s) %s", reply_code, reply_text
        )
        self._connection.ioloop.add_timeout(5, self.connect)

    def open_channel(self):
        LOG.info("Creating a new channel")
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        LOG.info("Channel opened")
        self._channel = channel
        self.setup_queue(self.queue)

    def setup_queue(self, queue_name):
        LOG.info("Declaring queue %s", queue_name)
        self._channel.queue_declare(queue_name,
                                    callback=self.on_queue_declareok,
                                    durable=True)

    def on_queue_declareok(self, method_frame):
        LOG.info("Queue declared successfully")

    def publish_message(self, message):
        if self._channel is None or not self._channel.is_open:
            # connection not available
            LOG.error("Failed to publish message. Rabbit connection not available")
            return

        self._channel.basic_publish(
            "",
            self.queue,
            json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )
