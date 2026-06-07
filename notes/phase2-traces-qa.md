# Phase 2 · Traces 学习笔记（Q&A）

> 实验完成后的理解校对与深度问答。

---

## ✅ 实验回顾与理解校对

### 我的理解
1. **实验 01 / 02**：trace_id、span_id 由 **Python SDK 内部随机生成**，通过 OTLP 推给 Collector → Jaeger 存储。后边的 curl 只是查询 Jaeger 的 HTTP API 来验证。
2. **实验 03**：成功看到跨进程关联（同一 traceID 串了 2 个进程的 3 个 span）。

### 校对结论
全部正确 ✅

---

## ❓ Q1：实验 03 中前后端是怎么关联的？（代码定位）

关联只靠两行代码：A 里 `inject()`、B 里 `extract()`。

### 🅰️ Server A —— "出门前把 trace 信息写在信封上"
[server_a.py](file:///home/jyan/otel-lab/phase2-traces/03_propagation_demo/server_a.py#L36-L41)

```python
headers = {}
inject(headers)          # ← 关键：把当前 trace context 写入 header
# 实际打印结果：
# headers = {'traceparent': '00-ffd26d585a068c01c033b64815c66e50-30ac9fafbf995a07-03'}
resp = http_lib.get("http://localhost:8002/process", headers=headers, timeout=5)
```

### 🅱️ Server B —— "到门口后，拆开信封看 trace 信息"
[server_b.py](file:///home/jyan/otel-lab/phase2-traces/03_propagation_demo/server_b.py#L24-L29)

```python
ctx = extract(request.headers)      # ← 关键 1：从 header 还原成 Context 对象

with tracer.start_as_current_span(
    "service-b.process",
    context=ctx,                    # ← 关键 2：显式把这个上下文当作父
    kind=SpanKind.SERVER,
    ...
) as span:
    ...
```

### 数据流（含代码行号）

```
┌─────────────────────── Server A 进程 ───────────────────────┐
│ start "service-a.start"          (trace_id=X)                │
│     start "service-a.call-b"     (trace_id=X)                │
│         inject(headers)                                       │
│         headers = {"traceparent":                             │
│             "00-X-<call-b的span_id>-03"}                      │
│         requests.get(url, headers=headers) ──────────────────┼──HTTP──┐
└──────────────────────────────────────────────────────────────┘        │
                                                                        ▼
┌─────────────────────── Server B 进程 ───────────────────────┐
│ ctx = extract(request.headers)                                │
│       # ctx 里含 trace_id=X, parent_span_id=call-b           │
│ start "service-b.process" with context=ctx                   │
│       # 新 span：                                              │
│       #   trace_id   = X（继承）                               │
│       #   parent_id  = call-b 的 span_id（继承）               │
│       #   span_id    = 新生成的                                 │
└──────────────────────────────────────────────────────────────┘
```

**关键洞察**：A 进程和 B 进程的 SDK 互不通信，全靠 HTTP header 里那 55 字符的字符串接力。

---

## ❓ Q2：Jaeger 瀑布图里怎么看 trace_id？

trace_id 显示在 UI 上，但位置藏得有点深：

| 方式 | 位置 | 说明 |
|---|---|---|
| 🅰️ **URL** | 浏览器地址栏 | `http://localhost:16686/trace/<完整trace_id>` —— **最可靠** |
| 🅱️ **顶部小字** | 瀑布图标题右侧 | 显示前 7 位缩写，hover 显示完整，点击可复制 |
| 🅲 **搜索框反查** | http://localhost:16686/search → "Lookup by Trace ID" | 粘贴 ID 查询 |
| 🅳 **span 详情** | 点开任一 span → 右上角 | 显示 SpanID 和所属 TraceID |

> 💡 老版本 Jaeger UI 字号小，新版（≥1.45）有改进。**用 URL 是最稳的方式**。

---

## ❓ Q3 自检题答案

### Q3.1 同进程内嵌套 span，谁是谁的父，靠什么机制传递？

**答**：靠 **Python `contextvars.ContextVar`**（OTel 内部叫 `Context`）。

机制：
- `start_as_current_span()` 干两件事：
  1. 创建 span
  2. 用 `context.attach()` 把它推入当前线程的 ContextVar 栈顶
- 在 `with` 块内调用 `trace.get_current_span()` → 拿到栈顶
- 嵌套调用 → 新 span 自动把栈顶当父
- `with` 结束时 `context.detach()` 弹栈

```python
with tracer.start_as_current_span("A") as a:        # 栈: [A]
    with tracer.start_as_current_span("B") as b:    # 栈: [A, B] → B 的父=A
        with tracer.start_as_current_span("C") as c:# 栈: [A, B, C] → C 的父=B
            pass
        # 栈: [A, B]
    # 栈: [A]
# 栈: []
```

⚠️ 注意：
- **异步 / 多线程**：ContextVar 自动随上下文切换，OTel 跟得上
- **子进程 fork**：必须重新初始化 provider，否则可能丢数据或重复

---

### Q3.2 跨进程时，trace context 走 HTTP 的哪个字段？格式？

**答**：HTTP header `traceparent`（W3C Trace Context 标准），可选 `tracestate`。

`traceparent` 格式（共 55 字符）：

```
traceparent: 00-ffd26d585a068c01c033b64815c66e50-30ac9fafbf995a07-03
             ↑  ↑                                ↑                ↑
             │  │                                │                │
             │  └ trace-id (16字节/32hex)         │                └ trace-flags (1字节)
             │                                    │                  bit0=sampled
             └ version (1字节, 当前 "00")          └ parent-id (8字节/16hex)
                                                    = 父 span 的 span_id
```

| 字段 | 含义 | 大小 |
|---|---|---|
| version | 协议版本，当前 `00` | 1 字节 |
| trace-id | 全局唯一 ID | 16 字节 |
| parent-id | 上游 span_id | 8 字节 |
| trace-flags | 标志位，bit0=sampled | 1 字节 |

附加 header `tracestate`（可选）：vendor-specific key=value 列表（Datadog / 阿里云等自定义）。

---

### Q3.3 SpanKind 为什么必须正确？错了会怎样？

**答**：SpanKind 是后端构建 **Service Map** 和 **RED 指标** 的依据。

| Kind | 含义 | 例子 |
|---|---|---|
| `SERVER` | 我作为服务端接收请求 | Flask/gRPC handler 入口 |
| `CLIENT` | 我作为客户端发起请求 | requests.get、DB 查询 |
| `PRODUCER` | 我把消息发给消息队列 | kafka producer.send |
| `CONSUMER` | 我从消息队列消费 | kafka consumer.poll |
| `INTERNAL` | 纯内部逻辑（默认） | 一段业务函数 |

错配的后果：
1. **Service Map 画错或断线**：Jaeger 通过 "A 的 CLIENT span 调到了 B 的 SERVER span" 来连线。CLIENT 写成 INTERNAL → A 和 B 不连线。
2. **延迟统计被污染**：CLIENT.duration = "我等了多久"；SERVER.duration = "我处理用了多久"。混淆就分不清。
3. **采样策略失效**：`tail_sampling` 经常按 SpanKind 决策（如"只保留有 SERVER root 的 trace"）。

---

### Q3.4 BatchSpanProcessor 程序退出时不 sleep 会发生什么？

**答**：**最后一批 span 会丢失**——还躺在内存队列里没被发出去。

原理：
- `BatchSpanProcessor` 把 span 攒在内存队列
- 满 **512 条** 或 等 **5 秒** 才触发一次 OTLP export
- Python 进程直接退出时，未达批量的 span 直接丢
- `01_hello_trace.py` 只产生 1 个 span，远不到 512，所以**必须等**

正确做法（生产环境别用 `sleep`）：

```python
# 方式 1：注册 atexit 优雅关闭
import atexit
atexit.register(provider.shutdown)   # 进程退出时强制 flush

# 方式 2：显式调用
provider.force_flush(timeout_millis=5000)
provider.shutdown()
```

学习阶段用 `time.sleep(3)` 简单粗暴够看效果；正式项目一定要 `shutdown`。

---

## 📌 一句话总结表

| 主题 | 关键词 | 一句话 |
|---|---|---|
| 同进程父子 | ContextVar 栈 | `start_as_current_span` 自动维护栈 |
| 跨进程父子 | `inject` / `extract` | HTTP header `traceparent` 串联 |
| Jaeger UI 看 trace_id | URL 或顶部小字 | URL 最可靠 |
| SpanKind | SERVER/CLIENT/INTERNAL/PRODUCER/CONSUMER | 决定 Service Map 和指标语义 |
| 程序退出丢 span | BatchSpanProcessor 队列 | 用 `provider.shutdown()` |
