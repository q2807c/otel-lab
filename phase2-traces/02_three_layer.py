"""
Phase 2 - Experiment 02: 三层嵌套 span

模拟一次真实 web 请求的调用链：
    web (handle_request)
      └── service (process_order)
            └── db (query_database)

学习要点：
  1. 嵌套 span：start_as_current_span 会自动把当前 span 设为父
  2. SpanKind：SERVER / INTERNAL / CLIENT 的区别
  3. duration 在 Jaeger 火焰图里的视觉效果
"""

import os
os.environ.setdefault("NO_PROXY", "localhost,127.0.0.1,::1")
for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
    os.environ.pop(k, None)

import time
import random
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# --- SDK 初始化 ---
provider = TracerProvider(resource=Resource.create({"service.name": "three-layer-demo"}))
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="localhost:4317", insecure=True))
)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)


def query_database(user_id: int) -> dict:
    """最底层：数据库查询"""
    with tracer.start_as_current_span(
        "db.query",
        kind=SpanKind.CLIENT,
        attributes={
            "db.system": "postgresql",
            "db.statement": "SELECT * FROM users WHERE id = ?",
            "db.user_id_param": user_id,
        },
    ) as span:
        time.sleep(random.uniform(0.02, 0.05))  # 模拟 DB 延迟
        span.add_event("rows_returned", {"count": 1})
        return {"id": user_id, "name": "Alice"}


def process_order(user_id: int) -> dict:
    """中间层：业务逻辑"""
    with tracer.start_as_current_span(
        "service.process_order",
        kind=SpanKind.INTERNAL,
        attributes={"order.user_id": user_id},
    ) as span:
        time.sleep(0.01)  # 模拟业务计算
        user = query_database(user_id)
        span.set_attribute("order.username", user["name"])
        return {"user": user, "items": ["book", "pen"]}


def handle_request(user_id: int):
    """最外层：模拟 HTTP server 入口"""
    with tracer.start_as_current_span(
        "web.handle_request",
        kind=SpanKind.SERVER,
        attributes={
            "http.method": "GET",
            "http.route": "/order",
            "http.user_id": user_id,
        },
    ) as span:
        try:
            result = process_order(user_id)
            span.set_attribute("http.status_code", 200)
            return result
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            span.set_attribute("http.status_code", 500)
            raise


if __name__ == "__main__":
    # 跑 3 次，每次都是一条完整的 3 层 trace
    for i in range(3):
        result = handle_request(user_id=i + 1)
        print(f"✅ 第 {i+1} 次请求完成: {result}")

    time.sleep(3)  # 等 BatchSpanProcessor 导出
    print("\n去 Jaeger 看火焰图: http://localhost:16686")
    print("Service 选 three-layer-demo → Find Traces")