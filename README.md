# OpenTelemetry 学习实验室

本目录是基于 O'Reilly《Learning OpenTelemetry》一书 + 官方文档 (https://opentelemetry.io/docs/) 制定的从零到一的完整动手学习工程。所有实验均在本地 Linux 环境完成，使用 Python 作为主要插桩语言，Docker Compose 编排可观测性后端 (Jaeger + Prometheus + Grafana + Loki + Kafka)。

## 目录结构

```
/data/otel-lab/
├── README.md                  # 本文件，工程总览
├── LEARNING_PLAN.md           # 主学习计划（8 阶段 / 8 周）
├── PROGRESS.md                # 周进度跟踪表
├── TROUBLESHOOTING.md         # 故障排查指南
├── docs/                      # 摘录、笔记、概念图
├── docker/                    # Collector / 后端 docker-compose 与配置
│   ├── docker-compose.yml
│   ├── otel-collector-config.yaml
│   ├── prometheus.yml
│   └── grafana/
├── apps/                      # 被插桩的示例应用
│   # Grafana 宿主机端口：3030（容器内仍 3000，宿主机 3000 已被占用）
│   ├── flask-api/
│   ├── fastapi-grpc/
│   ├── db-cache/
│   └── kafka-producer-consumer/
├── scripts/                   # 环境初始化、健康检查脚本
├── phase1-setup/              # 阶段 1：基础与环境
├── phase2-traces/             # 阶段 2：Traces
├── phase3-metrics/            # 阶段 3：Metrics
├── phase4-logs/               # 阶段 4：Logs
├── phase5-collector/          # 阶段 5：Collector 深入
├── phase6-instrumentation/    # 阶段 6：自动 / 手动插桩
├── phase7-integration/        # 阶段 7：DB / 消息队列 / gRPC
├── phase8-capstone/           # 阶段 8：综合项目
└── notes/                     # 自由笔记
```

## 快速开始

1. 阅读 [LEARNING_PLAN.md](./LEARNING_PLAN.md) 了解整体路径
2. 进入 `phase1-setup/` 完成环境准备
3. 按周推进，在 `PROGRESS.md` 中打勾记录
4. 遇到问题查阅 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
