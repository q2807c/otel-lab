"""
共享的 OTel 初始化代码（供 server_a 和 server_b 使用）

用法：
  from otel_init import init_tracer
  tracer = init_tracer("service-a")
"""
import os
os.environ.setdefault("NO_PROXY", "localhost,127.0.0.1,::1")
for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
    os.environ.pop(k, None)

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


def init_tracer(service_name: str):
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint="localhost:4317", insecure=True))
    )
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)