# Phase 4 · Logs 与三信号关联

## 目标
- 用 OTel LoggingHandler 把标准 logging 桥接到 OTel
- 让日志自动带上 trace_id / span_id
- Loki 中按 trace_id 跳转到 Jaeger

## 骨架
```python
import logging
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource

provider = LoggerProvider(resource=Resource.create({"service.name": "log-demo"}))
provider.add_log_record_processor(
    BatchLogRecordProcessor(OTLPLogExporter(endpoint="localhost:4317", insecure=True))
)
set_logger_provider(provider)

handler = LoggingHandler(level=logging.INFO, logger_provider=provider)
logging.basicConfig(level=logging.INFO, handlers=[handler])
log = logging.getLogger("demo")

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("work"):
    log.info("processing user request user_id=42")
```

## 验证
- [ ] Grafana → Loki Explore：`{service_name="log-demo"}` 可查
- [ ] 任意一条日志展开后含 `trace_id`、`span_id`
- [ ] 点 derived field 跳转到 Jaeger 对应 trace

## 自检题
1. OTel Logs 与传统 logging 最大差异是？
2. 为什么推荐 LoggingHandler 而不是直接调 Log API？
3. Loki 的 label 与 OTel attribute 关系？
4. 高基数 label 为什么对 Loki 致命？
5. 如何控制日志体积避免压垮 Collector？
