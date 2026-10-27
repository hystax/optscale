import contextlib
import sys
import types
from collections.abc import MutableMapping
from types import SimpleNamespace
from typing import Any

from pytest_mock import MockerFixture

import tools.optscale_telemetry.kombu_instrumentor as kombu_instrumentor_module
from tools.optscale_telemetry.kombu_instrumentor import KombuInstrumentor


def test_wrap_publish_injects_trace_headers(mocker: MockerFixture) -> None:
    instrumentor = KombuInstrumentor()
    tracer = mocker.Mock()
    tracer.start_as_current_span.return_value = contextlib.nullcontext()
    instrumentor._tracer = tracer

    def inject_headers(headers: MutableMapping[str, Any]) -> None:
        headers["traceparent"] = "injected-traceparent"

    inject_mock = mocker.patch(
        "tools.optscale_telemetry.kombu_instrumentor.propagate.inject",
        side_effect=inject_headers,
    )

    call_wrapped = mocker.Mock(return_value="published")
    producer = SimpleNamespace(exchange="events", routing_key="jobs")
    headers: dict[str, Any] = {}

    result = instrumentor._wrap_publish(
        call_wrapped=call_wrapped,
        instance=producer,
        args=(b"payload",),
        kwargs={"headers": headers},
    )

    assert result == "published"
    inject_mock.assert_called_once_with(headers)
    assert "traceparent" in headers


def test_wrap_receive_extracts_trace_headers(mocker: MockerFixture) -> None:
    instrumentor = KombuInstrumentor()
    tracer = mocker.Mock()
    tracer.start_as_current_span.return_value = contextlib.nullcontext()
    instrumentor._tracer = tracer

    parent_context = object()
    extract_mock = mocker.patch(
        "tools.optscale_telemetry.kombu_instrumentor.propagate.extract",
        return_value=parent_context,
    )

    message_headers = {"traceparent": "00-abc-def-01"}
    message = SimpleNamespace(
        headers=message_headers,
        delivery_info={"routing_key": "jobs"},
        properties={},
        body=b"payload",
        delivery_tag="tag-1",
    )
    consumer = SimpleNamespace(queues=[])
    call_wrapped = mocker.Mock(return_value="consumed")

    result = instrumentor._wrap_receive(
        call_wrapped=call_wrapped,
        instance=consumer,
        args=(None, message),
        kwargs={},
    )

    assert result == "consumed"
    extract_mock.assert_called_once_with(message_headers)
    assert tracer.start_as_current_span.call_args.kwargs["context"] is parent_context



def test_instrument_sets_tracer_and_wraps_publish_receive(
    mocker: MockerFixture,
) -> None:
    producer_class = type("Producer", (), {})
    consumer_class = type("Consumer", (), {})

    fake_messaging_module = types.ModuleType("kombu.messaging")
    fake_messaging_module.Producer = producer_class
    fake_messaging_module.Consumer = consumer_class

    fake_kombu_module = types.ModuleType("kombu")
    fake_kombu_module.messaging = fake_messaging_module

    mocker.patch.dict(
        sys.modules,
        {"kombu": fake_kombu_module, "kombu.messaging": fake_messaging_module},
    )

    tracer_provider = object()
    tracer = object()

    get_tracer_mock = mocker.patch(
        "tools.optscale_telemetry.kombu_instrumentor.trace.get_tracer",
        return_value=tracer,
    )
    wrap_mock = mocker.patch(
        "tools.optscale_telemetry.kombu_instrumentor.wrap_function_wrapper",
    )

    instrumentor = KombuInstrumentor()
    instrumentor._instrument(tracer_provider=tracer_provider)

    assert instrumentor._tracer is tracer
    get_tracer_mock.assert_called_once_with(
        kombu_instrumentor_module.__name__,
        tracer_provider=tracer_provider,
    )
    assert wrap_mock.call_args_list == [
        mocker.call(producer_class, "publish", instrumentor._wrap_publish),
        mocker.call(consumer_class, "receive", instrumentor._wrap_receive),
    ]


def test_uninstrument_unwraps_publish_and_receive(
    mocker: MockerFixture,
) -> None:
    producer_class = type("Producer", (), {})
    consumer_class = type("Consumer", (), {})

    fake_messaging_module = types.ModuleType("kombu.messaging")
    fake_messaging_module.Producer = producer_class
    fake_messaging_module.Consumer = consumer_class

    fake_kombu_module = types.ModuleType("kombu")
    fake_kombu_module.messaging = fake_messaging_module

    mocker.patch.dict(
        sys.modules,
        {"kombu": fake_kombu_module, "kombu.messaging": fake_messaging_module},
    )

    unwrap_mock = mocker.patch(
        "tools.optscale_telemetry.kombu_instrumentor.unwrap",
    )

    instrumentor = KombuInstrumentor()
    instrumentor._uninstrument()

    assert unwrap_mock.call_args_list == [
        mocker.call(producer_class, "publish"),
        mocker.call(consumer_class, "receive"),
    ]
