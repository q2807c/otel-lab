#!/usr/bin/env bash
# Phase 1 环境初始化脚本
# 用法：bash /data/otel-lab/scripts/setup_env.sh

set -euo pipefail

LAB_ROOT="/data/otel-lab"
cd "${LAB_ROOT}"

echo "[1/5] 检查基础工具..."
for cmd in python3 docker; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "  缺少 $cmd，请先安装" >&2
    exit 1
  fi
done

if ! docker compose version >/dev/null 2>&1; then
  echo "  缺少 docker compose v2，请安装 docker-compose-plugin" >&2
  exit 1
fi

echo "[2/5] 创建 Python 虚拟环境 (venv)..."
if [ ! -d "${LAB_ROOT}/.venv" ]; then
  python3 -m venv "${LAB_ROOT}/.venv"
fi
# shellcheck disable=SC1091
source "${LAB_ROOT}/.venv/bin/activate"
pip install --upgrade pip wheel

echo "[3/5] 安装 OpenTelemetry Python SDK 与常用插桩包..."
pip install \
  "opentelemetry-api>=1.27.0" \
  "opentelemetry-sdk>=1.27.0" \
  "opentelemetry-exporter-otlp>=1.27.0" \
  "opentelemetry-instrumentation>=0.48b0" \
  "opentelemetry-distro>=0.48b0"

# 自动安装当前环境匹配的 instrumentation
opentelemetry-bootstrap -a install || true

echo "[4/5] 启动 docker-compose 后端..."
cd "${LAB_ROOT}/docker"

# 若存在代理环境变量，提示一下
if [ -n "${HTTP_PROXY:-${http_proxy:-}}" ]; then
  echo "  检测到代理：${HTTP_PROXY:-${http_proxy:-}}"
fi

docker compose up -d
sleep 5
docker compose ps

echo "[5/5] 后端 URL："
echo "  Jaeger UI    : http://localhost:16686"
echo "  Prometheus   : http://localhost:9090"
echo "  Grafana      : http://localhost:3030 (admin/admin)"
echo "  Loki         : http://localhost:3100"
echo "  Collector    : OTLP gRPC=localhost:4317, HTTP=localhost:4318"
echo ""
echo "完成 ✅  下一步：cd ${LAB_ROOT}/phase1-setup && cat README.md"
