#!/usr/bin/env bash
# Claude through the Anthropic Messages API. The key goes in x-api-key, as the Anthropic SDKs send it.
set -euo pipefail
GW="${DCA_GATEWAY_URL:-https://ai-gateway-east-us1.azure-api.net/gateway}"
: "${DCA_GATEWAY_KEY:?set DCA_GATEWAY_KEY to your gateway key}"
curl -sS "$GW/anthropic/v1/messages" \
  -H "x-api-key: $DCA_GATEWAY_KEY" -H "anthropic-version: 2023-06-01" -H "Content-Type: application/json" \
  -d "{\"model\":\"${DCA_CLAUDE_DEPLOYMENT:-claude-sonnet-4-6}\",\"max_tokens\":64,\"messages\":[{\"role\":\"user\",\"content\":\"Name three oceans.\"}]}"
echo
