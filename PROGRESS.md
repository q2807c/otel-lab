# OpenTelemetry 学习进度跟踪表

> 用法：每完成一项就把 `[ ]` 改成 `[x]`。每周末写「本周收获」与「下周计划」。

## 总览

| 周 | 阶段 | 状态 | 完成日期 |
|----|------|------|----------|
| W1 | Phase 1 · 概念 + 环境 | [ ] | |
| W2 | Phase 2 · Traces | [ ] | |
| W3 | Phase 3 · Metrics | [ ] | |
| W4 | Phase 4 · Logs | [ ] | |
| W5 | Phase 5 · Collector | [ ] | |
| W6 | Phase 6 · Instrumentation | [ ] | |
| W7 | Phase 7 · 跨组件 | [ ] | |
| W8 | Phase 8 · Capstone | [ ] | |

---

## Week 1 · Phase 1
- [ ] 阅读《Learning OpenTelemetry》Ch.1–2
- [ ] `setup_env.sh` 一键起后端成功
- [ ] `health_check.sh` 全 ✅
- [ ] curl 推 span 在 Jaeger 可见
- [ ] 画出架构图到 `notes/phase1-arch.md`
- [ ] 完成 `phase1-setup/QUIZ.md`

**本周收获**：

**下周计划**：

---

## Week 2 · Phase 2
- [ ] 阅读 Ch.3 Traces 部分
- [ ] `01_hello_trace.py` 运行成功
- [ ] `02_three_layer.py` 三层 span 在 Jaeger 可见
- [ ] `03_propagation_demo` A→B 同 traceId
- [ ] 完成 QUIZ

**本周收获**：

**下周计划**：

---

## Week 3 · Phase 3
- [ ] 三个 metric 实验完成
- [ ] Prometheus 查到自定义指标
- [ ] Grafana RED 看板出图
- [ ] 完成 QUIZ

---

## Week 4 · Phase 4
- [ ] Logs 桥接成功
- [ ] 日志带 trace_id
- [ ] Loki → Jaeger 跳转成功
- [ ] 完成 QUIZ

---

## Week 5 · Phase 5
- [ ] 5 个 Collector 配置全部跑通
- [ ] tail_sampling 行为验证
- [ ] OTTL 脱敏验证
- [ ] 完成 QUIZ

---

## Week 6 · Phase 6
- [ ] Flask 自动插桩
- [ ] 手动插桩对比
- [ ] 自定义 Instrumentor
- [ ] 完成 QUIZ

---

## Week 7 · Phase 7
- [ ] DB + Redis 链路完整
- [ ] Kafka 跨进程 trace
- [ ] gRPC 跨服务 trace
- [ ] 完成 QUIZ

---

## Week 8 · Phase 8（毕业）
- [ ] 4 个微服务可运行
- [ ] Collector 高级配置生效
- [ ] Grafana 看板齐全
- [ ] 故障演练（≥2 场景）
- [ ] REPORT.md 完成（≥1500 字）

## 评估自评

| 能力 | 自评 (1–5) | 备注 |
|------|------------|------|
| Trace 模型理解 | | |
| Metric 模型理解 | | |
| Log 模型理解 | | |
| Collector 配置 | | |
| Python 插桩 | | |
| 故障定位 | | |
