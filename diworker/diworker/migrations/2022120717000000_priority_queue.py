from diworker.diworker.migrations.base import BaseMigration
from kombu import Exchange, Queue, Connection as QConnection
import logging
from retrying import retry
import amqp

LOG = logging.getLogger(__name__)
"""
Delete queue to support priorities
"""

QUEUE_NAME = "report-imports"


class NotDeleted(Exception):
    pass


def _retry(exc):
    if isinstance(exc, NotDeleted):
        return True
    return False


class Migration(BaseMigration):

    @property
    def connection_str(self):
        return 'amqp://{user}:{pass}@{host}:{port}'.format(
            **self.config_cl.read_branch('/rabbit'))

    def check_queue(self, mq_conn):
        # Get all queues
        vhost = "/"
        manager = mq_conn.get_manager()
        queues = manager.get_queues(vhost)

        for queue in queues:
            queue_name = queue["name"]
            if queue_name == QUEUE_NAME:
                LOG.info("Queue not deleted, retrying")
                raise NotDeleted("Not deleted")

    @retry(retry_on_exception=_retry, wait_fixed=0.05,
           stop_max_attempt_number=50)
    def delete_queue(self):
        with QConnection(self.connection_str) as conn:
            LOG.info("connecting to broker")
            # Create a channel
            LOG.info("getting channel")
            ch = conn.channel()
            try:
                ch.queue_purge(QUEUE_NAME)
                # drop queue
                LOG.info("deleting queue %s" % QUEUE_NAME)
                ch.queue_delete(QUEUE_NAME)
                LOG.info("deleted queue %s" % QUEUE_NAME)
            except amqp.exceptions.NotFound:
                pass
            finally:
                ch.close()
            self.check_queue(conn)

    def upgrade(self):
        self.delete_queue()

    def downgrade(self):
        self.delete_queue()
