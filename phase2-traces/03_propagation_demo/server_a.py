"""
Server A（调用方）

接收用户 HTTP 请求，然后调用 Server B。
关键：调用 B 前，要把当前 trace context 注入到 HTTP header（traceparent/tracestate）。

启动：
  python server_a.py    # 监听 :8001
然后另开一个终端：
  curl http://localhost:8001/start
"""
from otel_init import init_tracer
import requests as http_lib
from flask import Flask
from opentelemetry import trace
from opentelemetry.propagate import inject
from opentelemetry.trace import SpanKind

tracer = init_tracer("service-a")
app = Flask(__name__)


@app.get("/start")
def start():
    with tracer.start_as_current_span(
        "service-a.start",
        kind=SpanKind.SERVER,
        attributes={"http.method": "GET", "http.route": "/start"},
    ) as parent:
        # 调用下游前：起一个 CLIENT span 包裹 HTTP 调用
        with tracer.start_as_current_span(
            "service-a.call-b",
            kind=SpanKind.CLIENT,
            attributes={"http.url": "http://localhost:8002/process", "peer.service": "service-b"},
        ):
            headers = {}
            # 关键：把当前 trace context 写入 header
            inject(headers)
            # （顺便看一下注入了什么）
            print(f"   → 注入 header: {dict(headers)}")
            resp = http_lib.get("http://localhost:8002/process", headers=headers, timeout=5)
            return {
                "from_a": "ok",
                "from_b": resp.json(),
                "my_trace_id": format(parent.get_span_context().trace_id, "032x"),
            }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)