import atexit
import enum
import logging
from typing import Any

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import Span, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

LOG = logging.getLogger(__name__)


class OTELException(Exception):
    pass


class OpenTelemetryExporter(enum.StrEnum):
    CONSOLE = "console"
    OTLP = "otlp"
    AZURE_MONITOR = "azure_monitor"


class OpenTelemetryConfig:
    def __init__(
        self,
        *,
        service_name,
        service_version,
        otel_config,
        service_config,
        sqlalchemy_engine=None,
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.otel_config = otel_config
        self.service_config = service_config
        self.sqlalchemy_engine = sqlalchemy_engine
        self.enabled = False

    def setup_open_telemetry(self):
        if not self.otel_config:
            LOG.info("OTEL: no telemetry global configuration available.")
            return

        if self.otel_config.get("enabled", "").lower() != "true":
            LOG.info("OTEL: telemetry is not enabled.")

        if not self.service_config:
            LOG.info("OTEL: no telemetry service configuration available.")
            return

        otel_exporter = None
        exporter_type = None
        try:
            otel_exporter = self.otel_config["exporter"]
            exporter_type = OpenTelemetryExporter(otel_exporter["type"])
        except (KeyError, ValueError) as e:
            raise OTELException(
                f"OTEL: Invalid telemetry configuration. {type(e).__name__} - {e}."
            ) from e

        connection_string = otel_exporter.get("connection_string")

        if (
            exporter_type in (OpenTelemetryExporter.OTLP, OpenTelemetryExporter.AZURE_MONITOR)
            and not connection_string
        ):
            raise OTELException(
                f"OTEL: Invalid configuration. The exporter `{exporter_type.value}` "
                "requires a connection string."
            )

        resource = Resource(
            attributes={
                SERVICE_NAME: self.service_name,
                SERVICE_VERSION: self.service_version,
            }
        )
        tracer_provider = TracerProvider(resource=resource)

        if exporter_type == OpenTelemetryExporter.OTLP:
            span_exporter = OTLPSpanExporter(
                endpoint=connection_string,
            )

        elif exporter_type == OpenTelemetryExporter.AZURE_MONITOR:
            span_exporter = AzureMonitorTraceExporter(connection_string=connection_string)

        else:
            span_exporter = ConsoleSpanExporter()

        self.enabled = True
        LOG.info(f"OTEL: using the exporter `{exporter_type.value}`.")

        span_processor = BatchSpanProcessor(span_exporter)
        tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(tracer_provider)

        self.instrument_asyncio()
        self.instrument_threading()
        self.instrument_tornado()
        self.instrument_sqlalchemy()
        self.instrument_requests()
        self.instrument_urllib3()
        self.instrument_mongo()
        self.instrument_clickhouse()
        self.instrument_kombu()
        atexit.register(self.shutdown)

    def shutdown(self):
        if not self.enabled:
            return

        tracer_provider = trace.get_tracer_provider()
        if hasattr(tracer_provider, "shutdown"):
            tracer_provider.shutdown()
            LOG.info("OTEL: tracer provider shutdown complete")

    def instrument_asyncio(self):
        if self.service_config.get("enable_asyncio", "").lower() != "true":
            return

        from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor

        AsyncioInstrumentor().instrument()
        LOG.info("OTEL: `asyncio` as been instrumented.")

    def instrument_mongo(self):
        if self.service_config.get("enable_mongo", "").lower() != "true":
            return

        from opentelemetry.instrumentation.pymongo import PymongoInstrumentor

        PymongoInstrumentor().instrument(capture_statement=True)
        LOG.info("OTEL: `pymongo` as been instrumented.")

    def instrument_requests(self):
        if self.service_config.get("enable_requests", "").lower() != "true":
            return

        from opentelemetry.instrumentation.requests import RequestsInstrumentor

        RequestsInstrumentor().instrument()
        LOG.info("OTEL: `requests` as been instrumented.")

    def instrument_kombu(self):
        if self.service_config.get("enable_kombu", "true").lower() != "true":
            return

        from tools.optscale_telemetry.kombu_instrumentor import KombuInstrumentor

        KombuInstrumentor().instrument()
        LOG.info("OTEL: `kombu` as been instrumented.")

    def instrument_clickhouse(self):
        if self.service_config.get("enable_clickhouse", "true").lower() != "true":
            return

        from tools.optscale_telemetry.clickhouse_instrumentor import ClickHouseInstrumentor
        ClickHouseInstrumentor().instrument()

        LOG.info("OTEL: `clickhouse` as been instrumented.")

    def instrument_sqlalchemy(self):
        if self.service_config.get("enable_sqlalchemy", "").lower() != "true":
            return
        if not self.sqlalchemy_engine:
            raise OTELException(
                "OTEL: Invalid configuration. SQLAlchemy is enabled for the "
                f"service `{self.service_name}` but no engine has been provided."
            )

        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        SQLAlchemyInstrumentor().instrument(engine=self.sqlalchemy_engine, enable_commenter=True)
        LOG.info("OTEL: `sqlalchemy` as been instrumented.")

    def instrument_threading(self):
        if self.service_config.get("enable_threading", "").lower() != "true":
            return

        from opentelemetry.instrumentation.threading import ThreadingInstrumentor

        ThreadingInstrumentor().instrument()
        LOG.info("OTEL: `threading` as been instrumented.")

    def instrument_tornado(self):
        if self.service_config.get("enable_tornado", "").lower() != "true":
            return

        from opentelemetry.instrumentation.tornado import TornadoInstrumentor

        TornadoInstrumentor().instrument()
        LOG.info("OTEL: `tornado` as been instrumented.")

    def instrument_urllib3(self):
        if self.service_config.get("enable_urllib3", "").lower() != "true":
            return

        from opentelemetry.instrumentation.urllib3 import RequestInfo, URLLib3Instrumentor
        from urllib3.connectionpool import HTTPConnectionPool

        def urllib3_request_hook(
            span: Span,
            pool: HTTPConnectionPool,
            request_info: RequestInfo,
        ) -> Any:
            if not span or not span.is_recording():
                return

            url = request_info.url.lower()

            if "clickhouse" in url:
                span.set_attribute("peer.service", "clickhouse")
                span.set_attribute("db.system", "clickhouse")
                span.update_name("HTTP clickhouse")
                return

            if "etcd" in url:
                span.set_attribute("peer.service", "etcd")
                span.set_attribute("component", "etcd")
                span.update_name("HTTP etcd")
                return

        URLLib3Instrumentor().instrument(
            request_hook=urllib3_request_hook,
        )
        LOG.info("OTEL: `urllib3` as been instrumented.")
