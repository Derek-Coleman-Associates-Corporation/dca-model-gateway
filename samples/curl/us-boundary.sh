#!/usr/bin/env bash
# Keep a request inside the United States data boundary: only deployments you declared as US data zone are used;
# anything else is refused with 422 and never rerouted.
set -euo pipefail
GW="${DCA_GATEWAY_URL:-https://ai-gateway-east-us1.azure-api.net/gateway}"
: "${DCA_GATEWAY_KEY:?set DCA_GATEWAY_KEY to your gateway key}"
curl -sS "$GW/openai/v1/chat/completions" \
  -H "api-key: $DCA_GATEWAY_KEY" -H "Content-Type: application/json" -H "x-dca-data-boundary: us" \
  -d '{"messages":[{"role":"user","content":"Reply with OK"}],"max_completion_tokens":8}' \
  -D - | grep -iE '^HTTP|^x-dca-(model|data-boundary|processing-scope)|"code"|"content"'
