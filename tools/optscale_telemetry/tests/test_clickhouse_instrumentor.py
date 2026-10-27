import contextlib
import sys
import types
from types import SimpleNamespace

from pytest_mock import MockerFixture

import tools.optscale_telemetry.clickhouse_instrumentor as clickhouse_instrumentor_module
from tools.optscale_telemetry.clickhouse_instrumentor import ClickHouseInstrumentor


def test_wrap_query_creates_span_with_statement(mocker: MockerFixture) -> None:
    instrumentor = ClickHouseInstrumentor()
    tracer = mocker.Mock()
    tracer.start_as_current_span.return_value = contextlib.nullcontext()
    instrumentor._tracer = tracer

    call_wrapped = mocker.Mock(return_value="ok")
    client = SimpleNamespace(host="localhost", port=8123)

    wrapper = instrumentor._make_wrapper("query")
    result = wrapper(
        call_wrapped=call_wrapped,
        instance=client,
        args=("SELECT 1",),
        kwargs={},
    )

    assert result == "ok"
    span_kwargs = tracer.start_as_current_span.call_args.kwargs
    assert span_kwargs["attributes"]["db.system"] == "clickhouse"
    assert span_kwargs["attributes"]["db.operation.name"] == "query"
    assert span_kwargs["attributes"]["db.statement"] == "SELECT 1"
    assert span_kwargs["attributes"]["server.address"] == "localhost:8123"


def test_wrap_insert_creates_span_with_table(mocker: MockerFixture) -> None:
    instrumentor = ClickHouseInstrumentor()
    tracer = mocker.Mock()
    tracer.start_as_current_span.return_value = contextlib.nullcontext()
    instrumentor._tracer = tracer

    call_wrapped = mocker.Mock(return_value="ok")
    client = SimpleNamespace(host="localhost", port=8443)

    wrapper = instrumentor._make_wrapper("insert")
    result = wrapper(
        call_wrapped=call_wrapped,
        instance=client,
        args=("expenses", [("a",)]),
        kwargs={},
    )

    assert result == "ok"
    span_kwargs = tracer.start_as_current_span.call_args.kwargs
    assert span_kwargs["attributes"]["db.collection.name"] == "expenses"
    assert "db.statement" not in span_kwargs["attributes"]


def test_instrument_sets_tracer_and_wraps_methods(mocker: MockerFixture) -> None:
    class HttpClient:
        def query(self):
            return None

        def command(self):
            return None

        def insert(self):
            return None

        def query_rows_stream(self):
            return None

    fake_httpclient_module = types.ModuleType("clickhouse_connect.driver.httpclient")
    fake_httpclient_module.HttpClient = HttpClient

    fake_driver_module = types.ModuleType("clickhouse_connect.driver")
    fake_driver_module.httpclient = fake_httpclient_module

    fake_clickhouse_connect_module = types.ModuleType("clickhouse_connect")
    fake_clickhouse_connect_module.driver = fake_driver_module

    mocker.patch.dict(
        sys.modules,
        {
            "clickhouse_connect": fake_clickhouse_connect_module,
            "clickhouse_connect.driver": fake_driver_module,
            "clickhouse_connect.driver.httpclient": fake_httpclient_module,
        },
    )

    tracer_provider = object()
    tracer = object()

    get_tracer_mock = mocker.patch(
        "tools.optscale_telemetry.clickhouse_instrumentor.trace.get_tracer",
        return_value=tracer,
    )
    wrap_mock = mocker.patch(
        "tools.optscale_telemetry.clickhouse_instrumentor.wrap_function_wrapper",
    )

    instrumentor = ClickHouseInstrumentor()
    instrumentor._instrument(tracer_provider=tracer_provider)

    assert instrumentor._tracer is tracer
    get_tracer_mock.assert_called_once_with(
        clickhouse_instrumentor_module.__name__,
        tracer_provider=tracer_provider,
    )
    assert wrap_mock.call_count == 4


def test_uninstrument_unwraps_methods(mocker: MockerFixture) -> None:
    class HttpClient:
        def query(self):
            return None

        def command(self):
            return None

        def insert(self):
            return None

        def query_rows_stream(self):
            return None

    fake_httpclient_module = types.ModuleType("clickhouse_connect.driver.httpclient")
    fake_httpclient_module.HttpClient = HttpClient

    fake_driver_module = types.ModuleType("clickhouse_connect.driver")
    fake_driver_module.httpclient = fake_httpclient_module

    fake_clickhouse_connect_module = types.ModuleType("clickhouse_connect")
    fake_clickhouse_connect_module.driver = fake_driver_module

    mocker.patch.dict(
        sys.modules,
        {
            "clickhouse_connect": fake_clickhouse_connect_module,
            "clickhouse_connect.driver": fake_driver_module,
            "clickhouse_connect.driver.httpclient": fake_httpclient_module,
        },
    )

    unwrap_mock = mocker.patch(
        "tools.optscale_telemetry.clickhouse_instrumentor.unwrap",
    )

    instrumentor = ClickHouseInstrumentor()
    instrumentor._uninstrument()

    assert unwrap_mock.call_count == 4
