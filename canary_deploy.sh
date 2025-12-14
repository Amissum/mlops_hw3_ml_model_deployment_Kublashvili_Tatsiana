#!/bin/bash

# canary_deploy.sh - управление canary deployment

set -e

STAGE=${1:-"10"}  # 10%, 50%, 90%, 100%

echo "Starting Canary Deployment - Stage: ${STAGE}%"

update_weights() {
  local w1="$1"  # weight для service_v1
  local w2="$2"  # weight для service_v2

  awk -v w1="$w1" -v w2="$w2" '
    /weighted_clusters:/ { in_block=1; count=0; print; next }
    in_block && /weight:/ {
      count++
      if (count == 1) sub(/weight: [0-9]+/, "weight: " w1)
      else if (count == 2) sub(/weight: [0-9]+/, "weight: " w2)
    }
    { print }
  ' envoy.yaml > envoy.yaml.tmp && mv envoy.yaml.tmp envoy.yaml
}

case "$STAGE" in
  10)
    echo "Stage 1: 10% traffic to v2.0.0 (v1=90, v2=10)"
    update_weights 90 10
    ;;
  50)
    echo "Stage 2: 50% traffic to v2.0.0 (v1=50, v2=50)"
    update_weights 50 50
    ;;
  90)
    echo "Stage 3: 90% traffic to v2.0.0 (v1=10, v2=90)"
    update_weights 10 90
    ;;
  100)
    echo "Stage 4: 100% traffic to v2.0.0 (v1=0, v2=100)"
    update_weights 0 100
    ;;
  rollback)
    echo "ROLLBACK: 100% traffic to v1.0.0 (v1=100, v2=0)"
    update_weights 100 0
    ;;
  *)
    echo "Usage: $0 {10|50|90|100|rollback}"
    exit 1
    ;;
esac

docker compose -f docker-compose.canary.envoy.yaml restart envoy

echo "Deployment stage ${STAGE} completed!"
echo "Check Envoy admin: http://localhost:9901"