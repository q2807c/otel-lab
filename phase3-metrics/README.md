# Phase 3 · Metrics

## 目标
理解 6 种 Metric Instrument，配置 PeriodicExportingMetricReader，并在 Grafana 画第一张 RED 看板。

## 实验
| 文件 | 主题 |
|------|------|
| `01_counters.py` | Counter / UpDownCounter |
| `02_histogram_latency.py` | Histogram + 自定义 bucket |
| `03_observable_gauge.py` | Observable callback |

## 骨架
```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="localhost:4317", insecure=True),
    export_interval_millis=5000,
)
metrics.set_meter_provider(MeterProvider(
    resource=Resource.create({"service.name": "metrics-demo"}),
    metric_readers=[reader],
))

meter = metrics.get_meter(__name__)
req_counter = meter.create_counter("myapp_request_total", unit="1")
latency_hist = meter.create_histogram("myapp_request_duration_ms", unit="ms")

req_counter.add(1, {"route": "/hello", "status": "200"})
latency_hist.record(42.3, {"route": "/hello"})
```

## Grafana 看板（手动建）
- Panel 1: `sum(rate(myapp_request_total[1m])) by (route)` —— QPS
- Panel 2: `sum(rate(myapp_request_total{status=~"5.."}[1m]))` —— 错误率
- Panel 3: `histogram_quantile(0.95, sum(rate(myapp_request_duration_ms_bucket[5m])) by (le))` —— P95

## 验证
- [ ] http://localhost:9090/graph 查询自定义指标有数据
- [ ] Grafana 看板 3 个 Panel 全部出曲线
- [ ] 把 export_interval_millis 调到 1000，观察上报频率变化

## 自检题
1. 6 种 Instrument 各自适用场景？
2. Cumulative 和 Delta 哪个更适合 Prometheus？为什么？
3. Histogram bucket 边界设计原则？
4. ObservableGauge 与 Gauge 区别（OTel 1.x 之后）？
5. Exemplar 是什么？怎么把 trace_id 关联到 metric？
