# OpenTelemetry Lab · 故障排查指南

## 1. Docker 镜像拉不下来

**症状**：`docker compose up` 卡在 `Pulling ...` 或报 `i/o timeout`。

**方案 A：使用代理（你环境中已有 HTTP_PROXY/HTTPS_PROXY）**
```bash
# 配置 Docker daemon 走代理
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/proxy.conf <<EOF
[Service]
Environment="HTTP_PROXY=${HTTP_PROXY}"
Environment="HTTPS_PROXY=${HTTPS_PROXY}"
Environment="NO_PROXY=localhost,127.0.0.1,::1"
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

**方案 B：配置镜像加速**（如阿里云、DaoCloud）
```bash
sudo tee /etc/docker/daemon.json <<EOF
{ "registry-mirrors": ["https://docker.mirrors.ustc.edu.cn"] }
EOF
sudo systemctl restart docker
```

**方案 C：单独 docker pull 重试**
```bash
docker pull otel/opentelemetry-collector-contrib:0.111.0
```

---

## 2. Jaeger 看不到 trace

依次排查：
1. `docker compose logs otel-collector | tail -50` 是否有 export 失败
2. 应用日志中 OTLP 导出器是否报错（`Failed to export`）
3. 是否设置了 `service.name`（否则 Jaeger 中 service 列表无该名字）
4. 端口对不对：gRPC 用 `localhost:4317`，HTTP 用 `http://localhost:4318`（注意带 schema）
5. `insecure=True` 在本地未开启 TLS 时必须给

---

## 3. Prometheus 抓不到指标

1. 访问 http://localhost:8889/metrics 看 Collector 是否暴露
2. 访问 http://localhost:9090/targets 看 target 是否 UP
3. 指标命名是否被 Prometheus exporter 规范化（点变下划线）
4. Aggregation Temporality 是否为 Cumulative（Delta 在某些版本兼容不好）

---

## 4. Loki 报 `entry out of order` / `too far behind`

- 检查容器与宿主机时钟（`ntpdate` 或 `chronyc`）
- 调整 Collector batch processor `timeout` 至 ≤1s
- Loki 配置增大 `reject_old_samples_max_age`

---

## 5. Python 自动插桩报错

| 错误 | 解决 |
|------|------|
| `ImportError: No module named opentelemetry.instrumentation.flask` | `opentelemetry-bootstrap -a install` |
| `RuntimeError: Twice instrumented` | 自动 + 手动都做了，去掉一处 |
| span 不出现 | 检查是不是用了 `multiprocessing fork`，需要在 worker 启动后重新 init provider |

---

## 6. Collector OOM

- 加 `memory_limiter` processor，限制 `limit_mib`
- 减小 `batch.send_batch_size`
- 检查是否有 cardinality 爆炸的 attribute（user_id 直接成 label）

---

## 7. Kafka 容器启动失败

bitnami/kafka 3.x KRaft 模式对 listener 配置敏感，确认环境变量与本 compose 一致；若仍失败，改用 `bitnami/kafka:3.6` 版本试试。

---

## 8. Grafana 数据源连接失败

- 容器内访问对方需用服务名而非 `localhost`（如 `http://prometheus:9090`）
- 若改用 host 网络，注意端口冲突

---

## 9. 常用排查命令

```bash
docker compose ps
docker compose logs -f --tail=100 otel-collector
docker compose logs -f --tail=100 jaeger

# Collector 健康检查
curl http://localhost:13133/

# 看 Collector 自身指标
curl http://localhost:8888/metrics | grep otelcol_

# 强制清空所有数据重来
cd /data/otel-lab/docker && docker compose down -v && docker compose up -d
```

---

## 10. 还是搞不定？

1. 把出错日志贴到 CNCF Slack `#otel-collector` 或 `#otel-python`
2. 在 GitHub 仓库 issues 搜索关键字
3. 退回到 `phase1-setup` 的 curl 验证，证明后端没问题后再排查应用侧
