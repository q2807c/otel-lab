# Phase 7 · 跨组件端到端

## 目标
让 HTTP / gRPC / DB / Redis / Kafka 全部接入 OTel，验证同一 traceId 跨进程/跨组件传播。

## 子实验

### 7.1 FastAPI + SQLAlchemy + Redis
```bash
cd /data/otel-lab/apps/db-cache
pip install fastapi uvicorn sqlalchemy psycopg2-binary redis \
            opentelemetry-instrumentation-fastapi \
            opentelemetry-instrumentation-sqlalchemy \
            opentelemetry-instrumentation-redis

OTEL_SERVICE_NAME=db-cache opentelemetry-instrument uvicorn app:app --port 8001
```

构造流量：
```bash
curl http://localhost:8001/items/42   # 第一次 cache miss → DB → Redis SET
curl http://localhost:8001/items/42   # 第二次 cache hit
```

预期 Jaeger 中可看到：
- HTTP server span
- redis GET span（首次 miss 返回空）
- SQL SELECT span
- redis SET span

### 7.2 Kafka producer/consumer
```bash
pip install confluent-kafka opentelemetry-instrumentation-confluent-kafka
```

Producer 与 Consumer 分别为两个进程（不同 service.name），验证：
- Producer 的 `send` span 携带 `traceparent` 写入 message header
- Consumer 的 `poll` span 自动恢复上下文，进入同一 trace

### 7.3 gRPC
```bash
pip install grpcio grpcio-tools opentelemetry-instrumentation-grpc
```

写一个 EchoService，FastAPI 网关通过 gRPC 调后端，trace 中两个 service 串成一条。

## 验证
- [ ] 所有 service 出现在 Jaeger System Architecture 图
- [ ] DB span 含 `db.system=postgresql`、`db.statement` 已参数化
- [ ] Kafka 跨进程 trace 在同一 traceId
- [ ] gRPC trace 有 client/server 两个 span

## 自检题
1. SQL 参数化与 `db.statement` 关系？怎样避免敏感数据泄漏？
2. Kafka 怎样在 message 上携带 context？
3. Redis MULTI/EXEC 的 span 是几个？
4. gRPC streaming RPC 的 span 模型？
5. 大量 span 导致 Jaeger 卡顿时怎么办？
