"""
Server B（被调用方）

接收来自 Server A 的 HTTP 请求；从 HTTP header 中提取 W3C trace context，
然后在同一个 trace 下创建子 span。

启动：
  python server_b.py    # 监听 :8002
"""
from otel_init import init_tracer
import time
from flask import Flask, request
from opentelemetry import trace
from opentelemetry.propagate import extract
from opentelemetry.trace import SpanKind

tracer = init_tracer("service-b")
app = Flask(__name__)


@app.get("/process")
def process():
    # 从 HTTP header 提取上游 trace context（traceparent / tracestate）
    ctx = extract(request.headers)

    with tracer.start_as_current_span(
        "service-b.process",
        context=ctx,
        kind=SpanKind.SERVER,
        attributes={
            "http.method": "GET",
            "http.route": "/process",
            "peer.service": "service-a",
        },
    ) as span:
        time.sleep(0.05)
        span.add_event("computation_done")
        return {"result": "processed by service-b", "trace_id": format(span.get_span_context().trace_id, "032x")}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)