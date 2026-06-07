# Phase 1 · 环境搭建与概念入门

## 目标
- 理解 OTel 整体架构（API / SDK / Collector / Exporter / OTLP）
- 一键拉起本地后端套件
- 用一条 curl 直接向 Collector 推送 span 验证链路通畅

## 操作步骤

### 1. 一键初始化环境
```bash
bash /data/otel-lab/scripts/setup_env.sh
```

### 2. 健康检查
```bash
bash /data/otel-lab/scripts/health_check.sh
```

预期全部 ✅。若 ❌，参考 `/data/otel-lab/TROUBLESHOOTING.md`。

### 3. 用 curl 直推 OTLP span（不写一行代码先验证后端）
```bash
TRACE_ID=$(openssl rand -hex 16)
SPAN_ID=$(openssl rand -hex 8)
NOW_NS=$(date +%s%N)
END_NS=$((NOW_NS + 1000000))

curl -sS -X POST http://localhost:4318/v1/traces \
  -H 'Content-Type: application/json' \
  -d '{
    "resourceSpans": [{
      "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "curl-demo"}}]},
      "scopeSpans": [{
        "scope": {"name": "manual"},
        "spans": [{
          "traceId": "'"$TRACE_ID"'",
          "spanId": "'"$SPAN_ID"'",
          "name": "hello-from-curl",
          "kind": 1,
          "startTimeUnixNano": "'"$NOW_NS"'",
          "endTimeUnixNano": "'"$END_NS"'"
        }]
      }]
    }]
  }'
```

打开 http://localhost:16686 → 选择 service `curl-demo` → 应能看到一条 trace。

## 自检题（写到 QUIZ.md）
1. OTLP 的 gRPC 和 HTTP 端口分别是？两者差异？
2. `service.name` 属性的作用？放在 Resource 还是 Span？
3. Collector 三大组件是？为什么需要 `batch` processor？
4. Jaeger 1.35 后为什么不再需要 `jaeger` exporter 而用 `otlp`？
5. 画出本工程的数据流图（应用 → ? → ? → 后端）。
