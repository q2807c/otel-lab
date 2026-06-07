"""
Phase 2 - Experiment 01: 最小可工作 OTel trace

功能：
  创建一个单 span 通过 OTLP/gRPC 发送给 Collector → Jaeger

运行：
  source .venv/bin/activate
  python phase2-traces/01_hello_trace.py

预期输出：
  Span "hello-root" 在 Jaeger 中出现，service.name = hello-trace
"""

# ⚠️ 必须最早执行：避免 gRPC 把 localhost 也走 http_proxy
import os
os.environ.setdefault("NO_PROXY", "localhost,127.0.0.1,::1")
os.environ.setdefault("no_proxy", "localhost,127.0.0.1,::1")
# 兜底：直接清除（开发环境）
for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
    os.environ.pop(k, None)

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# 1. 定义资源（必填：service.name）
resource = Resource.create({"service.name": "hello-trace"})

# 2. 创建 TracerProvider 并绑定资源
provider = TracerProvider(resource=resource)

# 3. 添加 SpanProcessor：批量发送到 Collector（OTLP/gRPC）
#    本地 Collector 在 :4317，不启用 TLS
exporter = OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)

# 4. 设置全局 Tracer 提供者
trace.set_tracer_provider(provider)

# 5. 获取 Tracer 并创建一个 span
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("hello-root") as span:
    # 给 span 加点自定义属性
    span.set_attribute("demo.language", "python")
    span.set_attribute("demo.step", "01_hello_trace")

    # 记录一个事件（类似日志时间戳快照）
    span.add_event("program_start", {"msg": "Phase 2 begins!"})

    print("✅ Span 'hello-root' 已创建并发送")
    print("   去 Jaeger: http://localhost:16686 搜索 service=hello-trace")

# 6. 程序退出前等待导出完成（BatchSpanProcessor 有 5s 缓冲期）
import time
time.sleep(3)
print("   完成。已等待 3s 确保导出。")