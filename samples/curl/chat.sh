#!/usr/bin/env bash
# Chat completion with curl. No "model" in the body = your default deployment; add "model": "<deployment>" to pick one.
set -euo pipefail
GW="${DCA_GATEWAY_URL:-https://ai-gateway-east-us1.azure-api.net/gateway}"
: "${DCA_GATEWAY_KEY:?set DCA_GATEWAY_KEY to your gateway key}"
curl -sS "$GW/openai/v1/chat/completions" \
  -H "api-key: $DCA_GATEWAY_KEY" -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"In one sentence, what is an API gateway?"}],"max_completion_tokens":60}' \
  -D /dev/stderr
