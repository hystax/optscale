import os
import logging
from kombu import Connection, Exchange
from kombu.mixins import ConsumerProducerMixin
from kombu.utils.debug import setup_logging
from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient

RETRY_POLICY = {
    "max_retries": 15,
    "interval_start": 0,
    "interval_step": 1,
    "interval_max": 3,
}
EXCHANGE_NAME = "gemini-tasks"
QUEUE_NAME = "gemini-task"
TASK_EXCHANGE = Exchange(EXCHANGE_NAME, type="direct")
DEFAULT_ETCD_HOST = "etcd"
DEFAULT_ETCD_PORT = 80

LOG = logging.getLogger(__name__)


class Scheduler(ConsumerProducerMixin):
    def __init__(self, connection, config_client):
        self.connection = connection
        self.config_client = config_client
        self._rest_client = None

    @property
    def rest_client(self) -> RestClient:
        if self._rest_client is None:
            self._rest_client = RestClient(
                url=self.config_client.restapi_url(),
                secret=self.config_client.cluster_secret(),
            )
        return self._rest_client

    def _set_status(self, gemini_id: str, status: str) -> None:
        try:
            self.rest_client.gemini_update(gemini_id, {"status": status})
            LOG.info(f"Status updated to {status} for gemini {gemini_id}")
        except Exception as exc:
            LOG.exception(
                f"Not able to update status to {status} for gemini "
                f"{gemini_id}: {exc}"
            )
            raise exc

    def get_created_geminis(self) -> list:
        _, response = self.rest_client.gemini_list()

        geminis = response.get("geminis", [])

        created_geminis = list(
            filter(lambda gemini: gemini.get("status") == "CREATED", geminis)
        )

        return created_geminis

    def handle_message(self):
        created_geminis = self.get_created_geminis()

        for gemini in created_geminis:
            gemini_id = gemini.get("id")
            try:
                self._set_status(gemini_id, "QUEUED")

                self.producer.publish(
                    {"id": gemini_id},
                    serializer="json",
                    exchange=TASK_EXCHANGE,
                    declare=[TASK_EXCHANGE],
                    routing_key=QUEUE_NAME,
                    retry=True,
                    retry_policy=RETRY_POLICY,
                )
            except Exception as exc:
                LOG.exception(
                    f"Not able to publish message for gemini {gemini_id}: {exc}"
                )


def run(config_client: ConfigClient) -> None:
    conn_str = "amqp://{user}:{pass}@{host}:{port}".format(
        **config_client.read_branch("/rabbit")
    )
    with Connection(conn_str) as conn:
        try:
            scheduler = Scheduler(conn, config_client)
            LOG.info("Starting to produce...")
            scheduler.handle_message()
        except KeyboardInterrupt:
            LOG.info("Interrupted by user")


if __name__ == "__main__":
    setup_logging(loglevel="INFO", loggers=[""])

    config_client = ConfigClient(
        host=os.environ.get("HX_ETCD_HOST", DEFAULT_ETCD_HOST),
        port=int(os.environ.get("HX_ETCD_PORT", DEFAULT_ETCD_PORT)),
    )
    config_client.wait_configured()
    run(config_client)
