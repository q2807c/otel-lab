# OpenTelemetry 从零到一 · 8 周学习计划

> 主参考：O'Reilly **《Learning OpenTelemetry》** (Ted Young & Austin Parker)
> 官方文档：https://opentelemetry.io/docs/
> Python SDK 文档：https://opentelemetry-python.readthedocs.io/
> Collector 仓库：https://github.com/open-telemetry/opentelemetry-collector-contrib
> Demo 仓库：https://github.com/open-telemetry/opentelemetry-demo

---

## 0. 总体决策与前置条件

| 项目 | 选型 |
|------|------|
| 工作根目录 | `/data/otel-lab` |
| 主语言 | Python 3.11+ |
| 后端 | Jaeger (Traces) + Prometheus (Metrics) + Loki (Logs) + Grafana (统一面板) |
| 中间件 | PostgreSQL、Redis、Kafka（用于插桩练习） |
| 部署 | Docker + Docker Compose（镜像拉取失败时使用本机 env 中的 HTTP/HTTPS_PROXY） |
| 评估方式 | 每阶段「实验输出 + 验证清单 + 简答笔记」三件套 |

### 前置基础（不熟悉先补）

- Linux 基本命令、systemd、网络端口与抓包基础
- Python 虚拟环境、pip / uv、装饰器、异步基础
- Docker / Docker Compose 基本命令（`up -d`、`logs -f`、`exec`）
- HTTP / gRPC / Protobuf 基础概念
- 可观测性三大支柱（Traces、Metrics、Logs）的直觉认知

### 学习节奏建议

- 每周 8–10 小时（工作日 1h + 周末 4h）
- 每周读《Learning OpenTelemetry》对应章节 → 做实验 → 写 1 页笔记
- 实验代码全部提交到本地 git 仓库（`git init /data/otel-lab`）

---

## 1. 阶段路线总览

| 阶段 | 周 | 主题 | 关键产出 |
|------|----|------|----------|
| Phase 1 | W1 | 概念入门 + 环境搭建 | Compose 一键起全套后端 |
| Phase 2 | W2 | Traces：Span / Context / Propagation | 手写一个三层 trace |
| Phase 3 | W3 | Metrics：Counter / Histogram / Gauge | 自定义指标 → Prometheus 抓取 |
| Phase 4 | W4 | Logs + 关联（Trace ↔ Log） | 结构化日志带 traceId 进入 Loki |
| Phase 5 | W5 | Collector 深入（Receivers/Processors/Exporters） | 自定义 pipeline + Tail Sampling |
| Phase 6 | W6 | 自动插桩 vs 手动插桩 | Flask/FastAPI 零代码插桩对比 |
| Phase 7 | W7 | 数据库 / Redis / Kafka / gRPC 插桩 | 端到端跨服务 trace |
| Phase 8 | W8 | Capstone：微服务全链路可观测性 | 模拟故障 + 用 telemetry 定位 |

---

## 2. 各阶段详细计划

---

### Phase 1 · Week 1：概念与环境

**对应书本章节**：Ch.1 The State of Modern Observability、Ch.2 Why Use OpenTelemetry?

#### 学习目标
- 说清 Telemetry 三大信号定义、差异、使用场景
- 理解 OTel 的「数据模型 + API + SDK + Collector + 协议(OTLP)」分层架构
- 理解 OTLP 与 vendor-neutral 的设计动机
- 在本地一键拉起 Collector + Jaeger + Prometheus + Grafana + Loki

#### 步骤
1. 阅读书 Ch.1–2 + 官方 [Observability Primer](https://opentelemetry.io/docs/concepts/observability-primer/)
2. 在 `phase1-setup/` 完成：
   - 安装 Python 3.11、`uv` 或 venv
   - 安装 Docker / Docker Compose
   - 配置代理（若镜像拉取慢）：
     ```bash
     mkdir -p ~/.docker
     cat > ~/.docker/config.json <<EOF
     { "proxies": { "default": { "httpProxy": "${HTTP_PROXY}", "httpsProxy": "${HTTPS_PROXY}", "noProxy": "localhost,127.0.0.1" } } }
     EOF
     ```
3. 启动可观测性后端：
   ```bash
   cd /data/otel-lab/docker
   docker compose up -d
   docker compose ps
   ```
4. 浏览器验证：
   - Jaeger UI：http://localhost:16686
   - Prometheus：http://localhost:9090
   - Grafana：http://localhost:3030 （admin / admin，宿主机 3000 被占用故映射到 3030）
   - Loki：通过 Grafana 数据源验证

#### 验收标准
- [ ] `docker compose ps` 全部 `healthy`
- [ ] Grafana 三个数据源（Prometheus / Jaeger / Loki）均测试通过
- [ ] 能口述 OTel 架构图并画在 `notes/phase1-arch.md`
- [ ] 用一个 curl 命令向 Collector OTLP HTTP 4318 推送一个示例 span 并在 Jaeger 看到

---

### Phase 2 · Week 2：Traces 深入

**对应书本章节**：Ch.3 OpenTelemetry Overview（Traces 部分）、Ch.4 The OpenTelemetry Architecture

#### 学习目标
- 解释 Trace / Span / SpanContext / TraceFlags / Baggage 模型
- 掌握 W3C Trace Context 在 HTTP header 中的传播格式（`traceparent`、`tracestate`）
- 会用 Python SDK 创建 Tracer、起 Span、加 Attribute、加 Event、记录 Status
- 理解 BatchSpanProcessor vs SimpleSpanProcessor 差异

#### 步骤
1. 在 `phase2-traces/01_hello_trace.py` 写最小 trace 示例（导出到 OTLP）
2. 在 `02_three_layer.py` 实现 `web → service → db` 三层嵌套 span
3. 在 `03_propagation_demo/` 创建两个 Flask 服务 A 与 B，A 调用 B，验证 `traceparent` header 跨进程传播
4. 在 Jaeger 中查看完整火焰图，截图保存到 `notes/phase2-jaeger.png`

#### 示例命令与预期输出
```bash
cd /data/otel-lab/phase2-traces
python 01_hello_trace.py
# 预期：Jaeger UI 中能看到 service.name=hello-trace 的单 span trace
```

#### 验收标准
- [ ] 能在 Jaeger 看到自己制造的 3 层 trace，span kind 正确（SERVER / INTERNAL / CLIENT）
- [ ] A→B 跨进程 trace 在同一个 traceId 下展开
- [ ] 笔记中写出：BatchSpanProcessor 的批处理参数（`max_queue_size`、`schedule_delay_millis`）含义

---

### Phase 3 · Week 3：Metrics

**对应书本章节**：Ch.3（Metrics 部分）+ 官方 [Metrics Concepts](https://opentelemetry.io/docs/concepts/signals/metrics/)

#### 学习目标
- 区分 Counter、UpDownCounter、Histogram、Gauge、ObservableCounter
- 理解 Aggregation Temporality（Cumulative vs Delta）
- 配置 Periodic Exporting MetricReader → OTLP → Collector → Prometheus
- 在 Grafana 画第一张 RED（Rate/Errors/Duration）看板

#### 步骤
1. `phase3-metrics/01_counters.py`：HTTP 请求计数 + 错误计数
2. `02_histogram_latency.py`：用 Histogram 记录请求延迟，配置 explicit bucket boundaries
3. `03_observable_gauge.py`：用回调暴露当前活跃连接数
4. Collector pipeline 中启用 `prometheus` exporter，让 Prometheus 抓取
5. 在 Grafana 创建 dashboard 展示 P50/P95/P99 延迟与 QPS

#### 验收标准
- [ ] Prometheus 中可查询自定义指标 `myapp_request_total{}`
- [ ] Grafana 看板包含 QPS、Error Rate、Latency P95 三个 Panel
- [ ] 能解释为何 Histogram 用 explicit bucket 而非 summary
- [ ] 笔记说明 Cumulative vs Delta 的取舍

---

### Phase 4 · Week 4：Logs 与信号关联

**对应书本章节**：Ch.5 Instrumenting Applications（Logs 部分）

#### 学习目标
- 理解 OTel Logs Data Model（与 Traces / Metrics 共享 Resource & Context）
- 使用 Python `logging` 桥接到 OTel LoggerProvider
- 在日志记录中自动注入 `trace_id`、`span_id`
- 通过 Collector `loki` exporter 将日志送入 Loki，在 Grafana 中按 trace_id 跳转

#### 步骤
1. `phase4-logs/01_logging_bridge.py`：标准 logging → OTLPLogExporter
2. 在 Trace 上下文内打 log，验证日志带 trace 元数据
3. 在 Grafana Explore 中选中一条 log → 点击 `View trace`（Loki ↔ Tempo/Jaeger derived field）

#### 验收标准
- [ ] Loki 中能用 `{service_name="demo"} |= "ERROR"` 查询
- [ ] 任意一条 log 可一键跳到 Jaeger 对应 trace
- [ ] 笔记画出「Trace ↔ Log 关联示意图」

---

### Phase 5 · Week 5：Collector 深入

**对应书本章节**：Ch.6 The OpenTelemetry Collector（核心章节，重点精读）

#### 学习目标
- 掌握 Collector 三大组件：Receivers / Processors / Exporters / Connectors
- 部署模式：Agent（DaemonSet/sidecar） vs Gateway
- 关键 Processor：`batch`、`memory_limiter`、`attributes`、`resource`、`transform`、`filter`、`tail_sampling`
- 理解 Pipeline 的信号隔离（traces / metrics / logs 各一条 pipeline）

#### 步骤
1. 在 `phase5-collector/` 编写多个 `otel-collector-config-*.yaml`：
   - `01-basic.yaml`：otlp in → logging exporter（最小示例）
   - `02-multi-pipeline.yaml`：3 条 pipeline，分别送 Jaeger/Prometheus/Loki
   - `03-tail-sampling.yaml`：只采样 error trace + 1% 正常 trace
   - `04-transform.yaml`：用 OTTL 重写 attribute（脱敏）
2. 用 `otelcol-contrib --config=xxx.yaml` 启动验证
3. 用 `phase2-traces` 的客户端打流量，观察各 pipeline 输出差异

#### 验收标准
- [ ] tail_sampling 配置生效（Jaeger 中只看到 error + 抽样的正常 trace）
- [ ] OTTL transform 成功脱敏（如 `http.url` 中的 token 被替换为 `***`）
- [ ] 能画出 Collector 内部数据流图

---

### Phase 6 · Week 6：自动插桩 vs 手动插桩

**对应书本章节**：Ch.5 Instrumenting Applications、Ch.7 Designing a Telemetry Pipeline

#### 学习目标
- 区分 zero-code（auto）/ low-code / code-based 三种插桩方式
- 使用 `opentelemetry-instrument` CLI 对 Flask 应用零侵入插桩
- 找到并使用 `opentelemetry-instrumentation-{flask,requests,sqlalchemy,redis,kafka}` 等库
- 学会编写自定义 Instrumentation（继承 `BaseInstrumentor`）

#### 步骤
1. `apps/flask-api/`：原始 Flask 应用（无任何 OTel 代码）
2. 用 `opentelemetry-bootstrap -a install` 自动安装 instrumentation 包
3. 用 `opentelemetry-instrument --traces_exporter otlp --service_name flask-api flask run` 启动
4. 对比手动插桩版本（`apps/flask-api-manual/`）的 trace 详细度差异
5. 写一个简易自定义 Instrumentor 包装某个内部函数

#### 验收标准
- [ ] 自动插桩下 trace 包含 `http.method`、`http.route`、`http.status_code`
- [ ] 列出至少 3 个自动插桩与手动插桩的取舍（性能、控制粒度、维护成本）
- [ ] 自定义 Instrumentor 在 Jaeger 中可见

---

### Phase 7 · Week 7：跨组件端到端

**对应书本章节**：Ch.7、Ch.8 Rolling Out Observability

#### 学习目标
- 多语言/多组件下保持 trace 连续性
- 数据库（PostgreSQL via SQLAlchemy）、缓存（Redis）、消息队列（Kafka）、gRPC 调用链插桩
- 理解 Kafka producer/consumer 间的 context propagation（通过 message header）

#### 步骤
1. `apps/db-cache/`：FastAPI + SQLAlchemy + Redis，演示 cache miss → DB 查询的 trace
2. `apps/kafka-producer-consumer/`：producer 服务发消息，consumer 服务消费，验证同一 traceId
3. `apps/fastapi-grpc/`：FastAPI 网关 → gRPC 后端，两个 service.name 出现在同一 trace
4. 在 Grafana 创建 service map 视图（用 Jaeger 的 System Architecture）

#### 验收标准
- [ ] 数据库 span 含 `db.system`、`db.statement`（已脱敏参数）
- [ ] Kafka producer span 与 consumer span 在 Jaeger 中关联为同一 trace
- [ ] gRPC client/server span 完整
- [ ] 能解释 Kafka context propagation 在 message header 中的存放方式

---

### Phase 8 · Week 8：Capstone 综合项目

**对应书本章节**：Ch.8、Ch.9 Beyond Observability

#### 项目主题
**「订单系统全链路可观测性」**：

```
[client] → [api-gateway(FastAPI)] → [order-service(gRPC)]
                                       ├→ PostgreSQL
                                       ├→ Redis (库存缓存)
                                       └→ Kafka → [notify-service]
```

#### 任务
1. 实现上述四个 Python 微服务（最小可运行版本即可）
2. 全部接入 OTel（自动 + 关键路径手动 span）
3. 配置 Collector：tail sampling（保留所有 error + 5% 正常）、敏感字段脱敏
4. Grafana 看板：
   - RED 指标（每个服务）
   - 服务依赖拓扑
   - Trace 数 / Error trace 数
   - 日志聚合（按 service_name 分面板）
5. 故障注入演练：
   - 让 Redis 超时 → 观察延迟尖峰 + 跨服务 trace 中的瓶颈
   - 让 Kafka 不可用 → 观察 error trace 与日志告警
6. 写 `phase8-capstone/REPORT.md`：
   - 架构图
   - 关键截图
   - 用 telemetry 定位故障的过程
   - 个人总结：OTel 在生产环境落地的 3 个最佳实践、3 个陷阱

#### 验收标准（最终毕业标准）
- [ ] 四个服务全部接入并能正常出 trace/metric/log
- [ ] 至少 1 个故障场景能仅通过 telemetry（不看代码、不上服务器）定位根因
- [ ] 报告 ≥ 1500 字，含截图与命令记录
- [ ] 能在 5 分钟内向他人讲清 OTel 在该项目中的端到端数据流

---

## 3. 学习进度跟踪与评估

- **每日**：在 `notes/daily/YYYY-MM-DD.md` 写 3 行（今天做了什么 / 卡在哪 / 明天做什么）
- **每周末**：更新 [PROGRESS.md](./PROGRESS.md)，对照本周「验收标准」打勾
- **每阶段末**：写 1 页阶段总结放入 `phase{n}-*/SUMMARY.md`
- **自检题库**：每阶段附 5 道自测题（在各 phase 目录 `QUIZ.md`）

### 评估等级
| 等级 | 标准 |
|------|------|
| 入门 | 完成 Phase 1–3，能解释 traces/metrics 模型 |
| 熟练 | 完成 Phase 4–6，能独立配置 Collector pipeline |
| 进阶 | 完成 Phase 7–8，能在真实项目中落地 OTel |

---

## 4. 常见问题（详见 TROUBLESHOOTING.md）

- Docker 镜像拉不下来 → 使用 `HTTP_PROXY` / `HTTPS_PROXY` 环境变量
- Jaeger 看不到数据 → 检查 Collector 日志、检查 service.name 是否设置、检查 OTLP endpoint 是 `http://localhost:4317` (gRPC) 还是 `4318` (HTTP)
- Prometheus 抓不到指标 → 检查 Collector 的 `prometheus` exporter 暴露端口（默认 8889），并在 `prometheus.yml` 中配置 scrape target
- Loki 报 `entry out of order` → 时钟偏差或 batch 配置问题
- Python 自动插桩 ImportError → `opentelemetry-bootstrap -a install` 重装

---

## 5. 推荐资源

| 类型 | 资源 |
|------|------|
| 主教材 | 《Learning OpenTelemetry》O'Reilly |
| 官方文档 | https://opentelemetry.io/docs/ |
| Python SDK | https://opentelemetry-python.readthedocs.io/ |
| Collector | https://github.com/open-telemetry/opentelemetry-collector |
| Demo 项目 | https://github.com/open-telemetry/opentelemetry-demo |
| OTTL 语法 | https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/pkg/ottl |
| 社区 | CNCF Slack `#opentelemetry` 频道 |
| 视频 | KubeCon OTel 主题演讲（YouTube CNCF 频道） |
