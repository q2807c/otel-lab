# Phase 6 · 自动插桩 vs 手动插桩

## 目标
- 用 `opentelemetry-instrument` 给 Flask 应用零代码插桩
- 对比自动 vs 手动的取舍
- 编写自定义 Instrumentor

## 步骤

### 1. 准备最小 Flask 应用
```python
# apps/flask-api/app.py
from flask import Flask
app = Flask(__name__)

@app.get("/hello")
def hello():
    return {"msg": "hello"}
```

### 2. 自动插桩启动
```bash
cd /data/otel-lab/apps/flask-api
source ../../.venv/bin/activate
pip install flask opentelemetry-distro
opentelemetry-bootstrap -a install

OTEL_SERVICE_NAME=flask-api \
OTEL_TRACES_EXPORTER=otlp \
OTEL_METRICS_EXPORTER=otlp \
OTEL_LOGS_EXPORTER=otlp \
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
opentelemetry-instrument flask --app app run --port 8000
```

打几个 `curl http://localhost:8000/hello`，Jaeger 中应能看到含 `http.route=/hello` 的 trace。

### 3. 手动插桩对照
在 `flask-api-manual/` 中导入 SDK + 显式 `FlaskInstrumentor().instrument_app(app)`。

### 4. 自定义 Instrumentor
```python
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry import trace
from wrapt import wrap_function_wrapper

class MyLibInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self): return []
    def _instrument(self, **kwargs):
        tracer = trace.get_tracer(__name__)
        def wrapper(wrapped, instance, args, kwargs):
            with tracer.start_as_current_span(f"mylib.{wrapped.__name__}"):
                return wrapped(*args, **kwargs)
        wrap_function_wrapper("mylib", "do_work", wrapper)
    def _uninstrument(self, **kwargs): pass
```

## 验证
- [ ] 自动插桩出现 http.* / flask.* 属性
- [ ] 手动版与自动版 span 数量、属性差异列表
- [ ] 自定义 Instrumentor 的 span 出现在 Jaeger

## 自检题
1. 自动插桩底层依赖什么库做猴子补丁？
2. 何时必须手动插桩？
3. `OTEL_TRACES_SAMPLER` 支持哪些值？
4. 怎么禁用某个自动插桩库？
5. 多 worker (gunicorn) 下自动插桩需要注意什么？
