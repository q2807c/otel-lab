# Phase 2 · Traces 深入

## 目标
掌握 Trace / Span / Context Propagation，用 Python SDK 写出多层、多进程的 trace。

## 实验列表
| 文件 | 主题 |
|------|------|
| `01_hello_trace.py` | 最小可工作 trace，OTLP 导出 |
| `02_three_layer.py` | 嵌套 span：web → service → db |
| `03_propagation_demo/server_a.py` | Flask A 调 B，演示 W3C Trace Context 传播 |
| `03_propagation_demo/server_b.py` | Flask B 接收并继续 span |

## 关键代码骨架（`01_hello_trace.py`）
```python
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

resource = Resource.create({"service.name": "hello-trace"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="localhost:4317", insecure=True))
)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("root") as root:
    root.set_attribute("demo.kind", "hello")
    root.add_event("step-1")
```

## 运行
```bash
cd /data/otel-lab/phase2-traces
source ../.venv/bin/activate
python 01_hello_trace.py
# 等 5s 后到 Jaeger UI 查看
```

## 验证
- [ ] Jaeger 中能看到三层嵌套 span
- [ ] A→B 的 trace 同一 traceId
- [ ] span 上有自定义 attribute 与 event

## 自检题
1. SpanContext 包含哪些字段？哪些是不可变的？
2. `start_as_current_span` 和 `start_span` 区别？
3. `traceparent` header 的版本字段是什么？
4. Baggage 与 Attribute 的差异？
5. BatchSpanProcessor 的丢数据场景？
