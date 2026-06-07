# Phase 5 · Collector 深入

## 目标
- 区分 Agent / Gateway 部署
- 熟练编写 Collector pipeline
- 实现 tail sampling 与 OTTL transform

## 实验
| 配置文件 | 用途 |
|----------|------|
| `01-basic.yaml` | OTLP in → debug exporter |
| `02-multi-pipeline.yaml` | traces/metrics/logs 三 pipeline |
| `03-tail-sampling.yaml` | 保留 error + 10% 正常 trace |
| `04-transform.yaml` | OTTL 脱敏 + attribute 改写 |
| `05-routing.yaml` | 用 `routing` connector 把不同 service 路由到不同后端 |

## 关键片段：tail_sampling
```yaml
processors:
  tail_sampling:
    decision_wait: 10s
    num_traces: 50000
    expected_new_traces_per_sec: 100
    policies:
      - name: errors-policy
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: probabilistic-policy
        type: probabilistic
        probabilistic: { sampling_percentage: 10 }
```

## 关键片段：OTTL 脱敏
```yaml
processors:
  transform:
    trace_statements:
      - context: span
        statements:
          - replace_pattern(attributes["http.url"], "token=[^&]+", "token=***")
          - delete_key(attributes, "user.password")
```

## 验证
- [ ] 故意造 500 错误，tail sampling 后 100% 出现在 Jaeger
- [ ] 正常请求约 10% 出现
- [ ] OTTL 脱敏后 Jaeger 中 url 不含明文 token

## 自检题
1. tail vs head sampling 各自优缺点？
2. `memory_limiter` 应当放在 pipeline 首位还是末位？
3. Connector 与 Exporter 的区别？
4. Collector OOM 时的常见原因？
5. 怎么验证 Collector 配置语法（不实际启动）？
