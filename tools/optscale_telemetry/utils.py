from opentelemetry import trace


def get_trace_headers():
    ctx = trace.get_current_span().get_span_context()
    if not ctx.is_valid:
        return {}
    tid = format(ctx.trace_id, "032x")
    return {"x-trace-id": tid}
