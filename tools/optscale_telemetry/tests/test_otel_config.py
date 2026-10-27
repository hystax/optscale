import logging

import pytest
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pytest_mock import MockerFixture

from tools.optscale_telemetry import OpenTelemetryConfig, OTELException


@pytest.mark.parametrize(
    "otel_config", [{}, None]
)
def test_no_config(caplog: pytest.LogCaptureFixture, otel_config: dict | None):
    with caplog.at_level(logging.INFO):
        config = OpenTelemetryConfig(
            service_name="my service",
            service_version="1.0",
            otel_config=otel_config,
            service_config=None,
            sqlalchemy_engine=None,
        )
        config.setup_open_telemetry()

    assert "OTEL: no telemetry global configuration available." in caplog.text


@pytest.mark.parametrize(
    "otel_config",
    [
        {"exporter": "whatever"},
        {"enabled": "false"},
        {"enabled": "1"},
        {"enabled": "yes"},
    ],
)
def test_not_enabled(caplog: pytest.LogCaptureFixture, otel_config: dict):
    with caplog.at_level(logging.INFO):
        config = OpenTelemetryConfig(
            service_name="my service",
            service_version="1.0",
            otel_config=otel_config,
            service_config=None,
            sqlalchemy_engine=None,
        )
        config.setup_open_telemetry()

    assert "OTEL: telemetry is not enabled." in caplog.text



@pytest.mark.parametrize(
    "otel_config", [{"enabled": "true"}, {"enabled": "TRUE"}, {"enabled": "trUe"}]
)
@pytest.mark.parametrize(
    "service_config", [{}, None]
)
def test_no_service_config(
    caplog: pytest.LogCaptureFixture, otel_config: dict, service_config: dict | None,
):
    with caplog.at_level(logging.INFO):
        config = OpenTelemetryConfig(
            service_name="my service",
            service_version="1.0",
            otel_config=otel_config,
            service_config=service_config,
            sqlalchemy_engine=None,
        )
        config.setup_open_telemetry()

    assert "OTEL: no telemetry service configuration available." in caplog.text


def test_no_exporter():
    config = OpenTelemetryConfig(
        service_name="my service",
        service_version="1.0",
        otel_config={"enabled": "true"},
        service_config={"enable_requests": "true"},
        sqlalchemy_engine=None,
    )

    with pytest.raises(OTELException) as cv:
        config.setup_open_telemetry()

    assert str(cv.value) == "OTEL: Invalid telemetry configuration. KeyError - 'exporter'."

def test_no_exporter_type():
    config = OpenTelemetryConfig(
        service_name="my service",
        service_version="1.0",
        otel_config={"enabled": "true", "exporter": {}},
        service_config={"enable_requests": "true"},
        sqlalchemy_engine=None,
    )

    with pytest.raises(OTELException) as cv:
        config.setup_open_telemetry()

    assert str(cv.value) == "OTEL: Invalid telemetry configuration. KeyError - 'type'."


def test_invalid_exporter():
    config = OpenTelemetryConfig(
        service_name="my service",
        service_version="1.0",
        otel_config={"enabled": "true", "exporter": {"type": "wathever"}},
        service_config={"enable_requests": "true"},
        sqlalchemy_engine=None,
    )

    with pytest.raises(OTELException) as cv:
        config.setup_open_telemetry()

    assert str(cv.value) == (
        "OTEL: Invalid telemetry configuration. ValueError - 'wathever'"
        " is not a valid OpenTelemetryExporter."
    )


@pytest.mark.parametrize("exporter_type", ["otlp", "azure_monitor"])
def test_no_connection_string(exporter_type: str):
    config = OpenTelemetryConfig(
        service_name="my service",
        service_version="1.0",
        otel_config={"enabled": "true", "exporter": {"type": exporter_type}},
        service_config={"enable_requests": "true"},
        sqlalchemy_engine=None,
    )

    with pytest.raises(OTELException) as cv:
        config.setup_open_telemetry()

    assert str(cv.value) == (
        f"OTEL: Invalid configuration. The exporter `{exporter_type}` requires a connection string."
    )


def test_otlp_exporter(mocker: MockerFixture):
    m_span_processor = mocker.patch(
        "tools.optscale_telemetry.otel_config.BatchSpanProcessor",
        wraps=BatchSpanProcessor,
    )

    config = OpenTelemetryConfig(
        service_name="my service",
        service_version="1.0",
        otel_config={"enabled": "true", "exporter": {"type": "otlp", "connection_string": "http://localhost"}},
        service_config={"enable_requests": "true"},
        sqlalchemy_engine=None,
    )
    config.setup_open_telemetry()
    assert isinstance(m_span_processor.mock_calls[0].args[0], OTLPSpanExporter)
    config.shutdown()


def test_azure_exporter(mocker: MockerFixture):
    m_span_processor = mocker.patch(
        "tools.optscale_telemetry.otel_config.BatchSpanProcessor",
        wraps=BatchSpanProcessor,
    )

    config = OpenTelemetryConfig(
        service_name="my service",
        service_version="1.0",
        otel_config={
            "enabled": "true",
            "exporter": {
                "type": "azure_monitor",
                "connection_string": (
                    "InstrumentationKey=00000000-0000-0000-0000-000000000000;"
                    "IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/;"
                    "LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/;ApplicationId=my-app-id"
                ),
            },
        },
        service_config={"enable_requests": "true"},
        sqlalchemy_engine=None,
    )
    config.setup_open_telemetry()
    assert isinstance(m_span_processor.mock_calls[0].args[0], AzureMonitorTraceExporter)
    config.shutdown()


def test_console_exporter(mocker: MockerFixture):
    m_span_processor = mocker.patch(
        "tools.optscale_telemetry.otel_config.BatchSpanProcessor",
        wraps=BatchSpanProcessor,
    )

    config = OpenTelemetryConfig(
        service_name="my service",
        service_version="1.0",
        otel_config={
            "enabled": "true",
            "exporter": {
                "type": "azure_monitor",
                "connection_string": (
                    "InstrumentationKey=00000000-0000-0000-0000-000000000000;"
                    "IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/;"
                    "LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/;ApplicationId=my-app-id"
                ),
            },
        },
        service_config={"enable_requests": "true"},
        sqlalchemy_engine=None,
    )
    config.setup_open_telemetry()
    assert isinstance(m_span_processor.mock_calls[0].args[0], AzureMonitorTraceExporter)
    config.shutdown()


@pytest.mark.parametrize(
    ("enable_flag_name", "instrumentor_class"),
    [
        ("enable_asyncio", "opentelemetry.instrumentation.asyncio.AsyncioInstrumentor"),
        ("enable_threading", "opentelemetry.instrumentation.threading.ThreadingInstrumentor"),
        ("enable_tornado", "opentelemetry.instrumentation.tornado.TornadoInstrumentor"),
        ("enable_requests", "opentelemetry.instrumentation.requests.RequestsInstrumentor"),
        ("enable_urllib3", "opentelemetry.instrumentation.urllib3.URLLib3Instrumentor"),
        ("enable_mongo", "opentelemetry.instrumentation.pymongo.PymongoInstrumentor"),
        (
            "enable_clickhouse",
            "tools.optscale_telemetry.clickhouse_instrumentor.ClickHouseInstrumentor",
        ),
        ("enable_kombu", "tools.optscale_telemetry.kombu_instrumentor.KombuInstrumentor"),
    ],
)
@pytest.mark.parametrize(
    "enable_flag_value",
    ["true", "TRUE", "TruE"],
)
def test_instrument(
    mocker: MockerFixture,
    instrumentor_class: str,
    enable_flag_name: str,
    enable_flag_value: str,
):
    m_instrumentor = mocker.patch(instrumentor_class)

    config = OpenTelemetryConfig(
        service_name="svc",
        service_version="1.0",
        otel_config={"enabled": "true", "exporter": {"type": "console"}},
        service_config={enable_flag_name: enable_flag_value},
        sqlalchemy_engine=None,
    )
    config.setup_open_telemetry()

    m_instrumentor.assert_called_once()
    m_instrumentor.return_value.instrument.assert_called_once()
    config.shutdown()


@pytest.mark.parametrize(
    ("enable_flag_name", "instrumentor_class"),
    [
        ("enable_asyncio", "opentelemetry.instrumentation.asyncio.AsyncioInstrumentor"),
        ("enable_threading", "opentelemetry.instrumentation.threading.ThreadingInstrumentor"),
        ("enable_tornado", "opentelemetry.instrumentation.tornado.TornadoInstrumentor"),
        ("enable_requests", "opentelemetry.instrumentation.requests.RequestsInstrumentor"),
        ("enable_urllib3", "opentelemetry.instrumentation.urllib3.URLLib3Instrumentor"),
        ("enable_mongo", "opentelemetry.instrumentation.pymongo.PymongoInstrumentor"),
        (
            "enable_clickhouse",
            "tools.optscale_telemetry.clickhouse_instrumentor.ClickHouseInstrumentor",
        ),
        ("enable_kombu", "tools.optscale_telemetry.kombu_instrumentor.KombuInstrumentor"),
    ],
)
@pytest.mark.parametrize(
    "enable_flag_value",
    [
        "yes",
        "1",
        "false",
        "",
    ],
)
def test_instrument_disable(
    mocker: MockerFixture,
    instrumentor_class: str,
    enable_flag_name: str,
    enable_flag_value: str,
):
    m_instrumentor = mocker.patch(instrumentor_class)

    config = OpenTelemetryConfig(
        service_name="svc",
        service_version="1.0",
        otel_config={"enabled": "true", "exporter": {"type": "console"}},
        service_config={enable_flag_name: enable_flag_value},
        sqlalchemy_engine=None,
    )
    config.setup_open_telemetry()

    m_instrumentor.assert_not_called()
    m_instrumentor.return_value.instrument.assert_not_called()
    config.shutdown()
