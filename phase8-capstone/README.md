# Phase 8 · Capstone：订单系统全链路可观测性

## 架构

```
[client]
    │ GET /order/create?user=1&item=5
    ▼
[api-gateway (FastAPI)] ──OTLP──▶ Collector ──▶ Jaeger / Prometheus / Loki
    │
    ├─ gRPC ──▶ [order-service (gRPC)]
    │               ├─ SQLAlchemy → PostgreSQL
    │               └─ redis (库存缓存)
    │                        │ cache miss
    │                        ▼
    │               [psycopg2 → postgres stock table]
    │
    └─ Kafka ──▶ [notify-service (Kafka consumer)]
                     └─ 发送通知
```

## 实现步骤

### 1. 启动后端
```bash
cd /data/otel-lab/docker && docker compose up -d
```

### 2. 启动 Collector（tail sampling + transform）
```bash
# 启动时使用 phase8-collector-config.yaml
cd /data/otel-lab/docker
sed -i 's#otel-collector-config.yaml#../phase8-capstone/otel-collector-config.yaml#' docker-compose.yml
docker compose up -d otel-collector
```

### 3. 启动 4 个微服务
```bash
cd /data/otel-lab/phase8-capstone

# 终端 1: order-service (gRPC)
OTEL_SERVICE_NAME=order-service python order_service.py

# 终端 2: notify-service (Kafka consumer)
OTEL_SERVICE_NAME=notify-service python notify_service.py

# 终端 3: api-gateway (FastAPI)
OTEL_SERVICE_NAME=api-gateway python api_gateway.py
```

### 4. 造数
```bash
# 正常请求
python client.py --count 50

# 故障场景 1: Redis 压力
python client.py --count 200 --concurrent 20

# 故障场景 2: Kafka 不可用
# 需先 docker compose stop kafka
python client.py --count 10
```

### 5. 故障分析
| 故障 | Telemetry 现象 |
|------|----------------|
| Redis 慢 | order-service 中 redis span latency 突增 |
| Kafka 宕 | notify-service 日志 ERROR，Kafka send span 带 error |
| DB 连接池耗尽 | order-service 中 sqlalchemy span time out |
| 内存泄漏 | Collector 8888 指标 `process_memory_usage` 上升 |

## 产出交付
- [ ] `phase8-capstone/` 内 4 个微服务可运行
- [ ] Collector config：tail sampling + OTTL 脱敏
- [ ] Grafana dashboard 含 RED / 拓扑 / 日志面板
- [ ] `REPORT.md`（≥1500 字）：架构图、故障定位过程、最佳实践、陷阱