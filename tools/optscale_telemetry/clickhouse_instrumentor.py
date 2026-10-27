from __future__ import annotations

from collections.abc import Callable, Collection
from importlib import import_module
from typing import Any

from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.trace import SpanKind
from wrapt import wrap_function_wrapper

_CLICKHOUSE_DEPENDENCIES = ("clickhouse-connect >= 0.8.0, < 1.0.0",)
_WRAPPED_METHODS = ("query", "command", "insert", "query_rows_stream")


class ClickHouseInstrumentor(BaseInstrumentor):
    """Instrument clickhouse-connect HttpClient calls."""

    def instrumentation_dependencies(self) -> Collection[str]:
        """Return supported clickhouse-connect version ranges.

        Returns:
            Collection[str]: Supported clickhouse-connect versions.
        """
        return _CLICKHOUSE_DEPENDENCIES

    def _instrument(self, **kwargs: Any) -> None:
        """Patch clickhouse-connect client methods to create spans.

        Args:
            **kwargs: Optional instrumentation arguments from OpenTelemetry.
        """
        tracer_provider = kwargs.get("tracer_provider")
        self._tracer = trace.get_tracer(
            __name__,
            tracer_provider=tracer_provider,
        )
        HttpClient = _get_http_client_class()

        for method_name in _WRAPPED_METHODS:
            if hasattr(HttpClient, method_name):
                wrap_function_wrapper(HttpClient, method_name, self._make_wrapper(method_name))

    def _uninstrument(self, **kwargs: Any) -> None:
        """Remove clickhouse-connect method patches.

        Args:
            **kwargs: Optional uninstrument arguments from OpenTelemetry.
        """
        HttpClient = _get_http_client_class()

        for method_name in _WRAPPED_METHODS:
            if hasattr(HttpClient, method_name):
                unwrap(HttpClient, method_name)

    def _make_wrapper(self, operation: str) -> Callable[..., Any]:
        def _wrapper(
            call_wrapped: Callable[..., Any],
            instance: Any,
            args: tuple[Any, ...],
            kwargs: dict[str, Any],
        ) -> Any:
            attributes = _build_attributes(instance, operation, args, kwargs)
            with self._tracer.start_as_current_span(
                f"clickhouse.{operation}",
                kind=SpanKind.CLIENT,
                attributes=attributes,
            ):
                return call_wrapped(*args, **kwargs)

        return _wrapper


def _build_attributes(
    instance: Any,
    operation: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    attributes: dict[str, Any] = {
        "db.system": "clickhouse",
        "db.operation.name": operation,
        "peer.service": "clickhouse",
    }

    endpoint = _get_endpoint(instance)
    if endpoint is not None:
        attributes["server.address"] = endpoint

    statement = _get_statement(operation, args, kwargs)
    if statement is not None:
        attributes["db.statement"] = statement

    table_name = _get_table_name(operation, args, kwargs)
    if table_name is not None:
        attributes["db.collection.name"] = table_name

    return attributes


def _get_http_client_class() -> type[Any]:
    module = import_module("clickhouse_connect.driver.httpclient")
    return module.HttpClient


def _get_endpoint(instance: Any) -> str | None:
    host = getattr(instance, "host", None)
    port = getattr(instance, "port", None)
    if host in (None, ""):
        return None
    if port in (None, ""):
        return str(host)
    return f"{host}:{port}"


def _get_statement(
    operation: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str | None:
    if operation in ("query", "query_rows_stream"):
        query = kwargs.get("query")
        if query is None and args:
            query = args[0]
        if isinstance(query, str) and query:
            return query
        return None

    if operation == "command":
        command = kwargs.get("cmd")
        if command is None and args:
            command = args[0]
        if isinstance(command, str) and command:
            return command
        return None

    return None


def _get_table_name(
    operation: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str | None:
    if operation != "insert":
        return None

    table = kwargs.get("table")
    if table is None and args:
        table = args[0]
    if table in (None, ""):
        return None
    return str(table)
