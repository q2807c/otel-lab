#!/usr/bin/env bash
# 健康检查脚本，验证所有后端组件 OK
set -uo pipefail

check() {
  local name=$1 url=$2
  if curl -fsS --noproxy '*' -o /dev/null --max-time 3 "$url"; then
    echo "  ✅ $name  ($url)"
  else
    echo "  ❌ $name  ($url)"
  fi
}

echo "OpenTelemetry Lab 健康检查："
check "Collector health" "http://localhost:13133/"
check "Jaeger UI"        "http://localhost:16686/"
check "Prometheus"       "http://localhost:9090/-/ready"
check "Grafana"          "http://localhost:3030/api/health"
check "Loki ready"       "http://localhost:3100/ready"
