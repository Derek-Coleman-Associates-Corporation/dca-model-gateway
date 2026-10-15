#!/usr/bin/env bash
# One request per route; prints the status and the deployment the gateway chose (x-dca-model).
set -euo pipefail
GW="${DCA_GATEWAY_URL:-https://ai-gateway-east-us1.azure-api.net/gateway}"
: "${DCA_GATEWAY_KEY:?set DCA_GATEWAY_KEY to your gateway key}"
for route in cheap oss-only auto reasoning code frontier; do
  out=$(curl -sS -o /dev/null -D - -w '%{http_code}' "$GW/openai/v1/chat/completions" \
    -H "api-key: $DCA_GATEWAY_KEY" -H "Content-Type: application/json" -H "x-dca-route: $route" \
    -d '{"messages":[{"role":"user","content":"Reply with OK"}],"max_completion_tokens":8}')
  printf '%-10s %s %s\n' "$route" "${out: -3}" "$(grep -i '^x-dca-model:' <<<"$out" | tr -d '\r')"
done
