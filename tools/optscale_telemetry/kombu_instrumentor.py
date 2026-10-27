from __future__ import annotations

from collections.abc import Callable, Collection, MutableMapping, Sequence
from typing import Any

from opentelemetry import propagate, trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind
from wrapt import wrap_function_wrapper

_KOMBU_DEPENDENCIES = ("kombu >= 5.3.0, < 6.0.0",)
_MESSAGING_OPERATION = "messaging.operation"
_MESSAGING_DESTINATION_SUBSCRIPTION_NAME = (
    "messaging.destination.subscription.name"
)
_MESSAGING_RABBITMQ_DESTINATION_ROUTING_KEY = (
    "messaging.rabbitmq.destination.routing_key"
)


class KombuInstrumentor(BaseInstrumentor):
    """Instrument kombu producers and consumers.

    The instrumentor creates producer spans around message publishing,
    injects trace context into kombu headers, and creates consumer spans
    around callback processing using context extracted from inbound headers.
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        """Return the supported kombu dependency range.

        Returns:
            Collection[str]: Supported kombu versions for this instrumentor.
        """
        return _KOMBU_DEPENDENCIES

    def _instrument(self, **kwargs: Any) -> None:
        tracer_provider = kwargs.get("tracer_provider")
        self._tracer = trace.get_tracer(
            __name__,
            tracer_provider=tracer_provider,
        )

        from kombu.messaging import Consumer, Producer

        wrap_function_wrapper(Producer, "publish", self._wrap_publish)
        wrap_function_wrapper(Consumer, "receive", self._wrap_receive)

    def _uninstrument(self, **kwargs: Any) -> None:
        from kombu.messaging import Consumer, Producer

        unwrap(Producer, "publish")
        unwrap(Consumer, "receive")

    def _wrap_publish(
        self,
        call_wrapped: Callable[..., Any],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        headers, updated_args, updated_kwargs = _get_publish_headers(args, kwargs)
        exchange = _get_publish_exchange(instance, updated_args, updated_kwargs)
        routing_key = _get_publish_routing_key(instance, updated_args, updated_kwargs)
        destination_name = _get_publish_destination_name(exchange, routing_key)
        attributes = _build_common_attributes(
            destination_name,
            routing_key,
            operation="publish",
        )
        message_id = updated_kwargs.get("message_id")
        if message_id is not None:
            attributes[SpanAttributes.MESSAGING_MESSAGE_ID] = str(message_id)

        payload_size = _get_payload_size(updated_args[0] if updated_args else None)
        if payload_size is not None:
            attributes[SpanAttributes.MESSAGING_MESSAGE_PAYLOAD_SIZE_BYTES] = payload_size

        span_name = _get_span_name("publish", destination_name)

        with self._tracer.start_as_current_span(
            span_name,
            kind=SpanKind.PRODUCER,
            attributes=attributes,
        ):
            propagate.inject(headers)
            return call_wrapped(*updated_args, **updated_kwargs)

    def _wrap_receive(
        self,
        call_wrapped: Callable[..., Any],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        message = _get_receive_message(args, kwargs)
        headers = getattr(message, "headers", {}) or {}
        parent_context = propagate.extract(headers)
        destination_name = _get_consumer_destination_name(instance, message)
        routing_key = _get_message_routing_key(message)
        attributes = _build_common_attributes(
            destination_name,
            routing_key,
            operation="process",
        )
        subscription_name = _get_subscription_name(instance)
        if subscription_name is not None:
            attributes[_MESSAGING_DESTINATION_SUBSCRIPTION_NAME] = subscription_name

        message_id = _get_message_id(message)
        if message_id is not None:
            attributes[SpanAttributes.MESSAGING_MESSAGE_ID] = message_id

        payload_size = _get_payload_size(getattr(message, "body", None))
        if payload_size is not None:
            attributes[SpanAttributes.MESSAGING_MESSAGE_PAYLOAD_SIZE_BYTES] = payload_size

        span_name = _get_span_name("process", destination_name)

        with self._tracer.start_as_current_span(
            span_name,
            context=parent_context,
            kind=SpanKind.CONSUMER,
            attributes=attributes,
        ):
            return call_wrapped(*args, **kwargs)


def _get_publish_headers(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> tuple[MutableMapping[str, Any], tuple[Any, ...], dict[str, Any]]:
    headers = kwargs.get("headers")
    if headers is None and len(args) > 9:
        headers = args[9]

    if headers is None:
        headers = {}
    elif not isinstance(headers, MutableMapping):
        headers = dict(headers)

    updated_kwargs = dict(kwargs)
    if len(args) > 9:
        updated_args = list(args)
        updated_args[9] = headers
        return headers, tuple(updated_args), updated_kwargs

    updated_kwargs["headers"] = headers
    return headers, args, updated_kwargs


def _get_publish_routing_key(
    producer: Any,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str | None:
    routing_key = kwargs.get("routing_key")
    if routing_key is None and len(args) > 1:
        routing_key = args[1]
    if routing_key is None:
        routing_key = getattr(producer, "routing_key", None)
    if routing_key is None:
        return None
    return str(routing_key)


def _get_publish_exchange(
    producer: Any,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    exchange = kwargs.get("exchange")
    if exchange is None and len(args) > 11:
        exchange = args[11]
    if exchange is None:
        exchange = getattr(producer, "exchange", None)
    return exchange


def _get_publish_destination_name(exchange: Any, routing_key: str | None) -> str:
    exchange_name = _get_entity_name(exchange)
    if exchange_name:
        return exchange_name
    if routing_key:
        return routing_key
    return "default"


def _get_consumer_destination_name(instance: Any, message: Any) -> str:
    subscription_name = _get_subscription_name(instance)
    if subscription_name:
        return subscription_name

    exchange_name = _get_message_exchange(message)
    if exchange_name:
        return exchange_name

    routing_key = _get_message_routing_key(message)
    if routing_key:
        return routing_key

    return "default"


def _get_subscription_name(instance: Any) -> str | None:
    queues = getattr(instance, "queues", None)
    if not isinstance(queues, Sequence):
        return None

    queue_names = [name for name in (_get_entity_name(queue) for queue in queues) if name]
    if len(queue_names) == 1:
        return queue_names[0]
    return None


def _get_receive_message(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
    if "message" in kwargs:
        return kwargs["message"]
    if len(args) > 1:
        return args[1]
    return None


def _get_message_exchange(message: Any) -> str | None:
    delivery_info = getattr(message, "delivery_info", None) or {}
    exchange = delivery_info.get("exchange")
    if exchange in (None, ""):
        return None
    return str(exchange)


def _get_message_routing_key(message: Any) -> str | None:
    delivery_info = getattr(message, "delivery_info", None) or {}
    routing_key = delivery_info.get("routing_key")
    if routing_key in (None, ""):
        return None
    return str(routing_key)


def _get_message_id(message: Any) -> str | None:
    properties = getattr(message, "properties", None) or {}
    message_id = properties.get("message_id")
    if message_id is None:
        message_id = getattr(message, "delivery_tag", None)
    if message_id is None:
        return None
    return str(message_id)


def _build_common_attributes(
    destination_name: str,
    routing_key: str | None,
    operation: str,
) -> dict[str, Any]:
    attributes: dict[str, Any] = {
        SpanAttributes.MESSAGING_SYSTEM: "rabbitmq",
        SpanAttributes.MESSAGING_DESTINATION_NAME: destination_name,
        _MESSAGING_OPERATION: operation,
    }
    if routing_key is not None:
        attributes[_MESSAGING_RABBITMQ_DESTINATION_ROUTING_KEY] = routing_key
    return attributes


def _get_span_name(operation: str, destination_name: str) -> str:
    return f"{operation} {destination_name}"


def _get_entity_name(entity: Any) -> str | None:
    if entity is None:
        return None

    name = getattr(entity, "name", None)
    if name not in (None, ""):
        return str(name)

    if isinstance(entity, str) and entity:
        return entity

    return None


def _get_payload_size(body: Any) -> int | None:
    if body is None:
        return 0
    if isinstance(body, str):
        return len(body.encode("utf-8"))
    if isinstance(body, bytes):
        return len(body)
    try:
        return len(body)
    except TypeError:
        return None
