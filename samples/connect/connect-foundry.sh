#!/usr/bin/env bash
# One-time setup in YOUR Azure tenant so DCA Model Gateway can call your Azure AI Foundry resource without any key:
#   1. add the "DCA Model Gateway Connector" enterprise application to your Microsoft Entra tenant;
#   2. give it a role on ONE Foundry / Azure AI Services / Azure OpenAI resource:
#      - default: the custom role "DCA Model Gateway Inference" (data plane only: no keys, no settings), created in this
#        subscription from dca-model-gateway-inference-role.json if it does not exist yet;
#      - with --builtin-role: the built-in "Cognitive Services User" (also allows listing the resource's keys).
# Needs: Azure CLI signed in to the tenant and subscription that hold the resource, as a user who may create service
# principals (Application Administrator or Cloud Application Administrator) and roles/assignments (Owner or
# User Access Administrator).
# Usage: bash connect-foundry.sh <resource-group> <foundry-resource-name> [--builtin-role]
# Undo:  az role assignment delete --assignee 7154fd27-4506-4cd5-8e3a-b2e5208d0846 --scope <resource id>
set -euo pipefail
CONNECTOR_APP_ID="7154fd27-4506-4cd5-8e3a-b2e5208d0846"
RG="${1:?usage: connect-foundry.sh <resource-group> <foundry-resource-name> [--builtin-role]}"
NAME="${2:?usage: connect-foundry.sh <resource-group> <foundry-resource-name> [--builtin-role]}"
ROLE="DCA Model Gateway Inference"
[ "${3:-}" = "--builtin-role" ] && ROLE="Cognitive Services User"
HERE="$(cd "$(dirname "$0")" && pwd)"

if az ad sp show --id "$CONNECTOR_APP_ID" --query id -o tsv >/dev/null 2>&1; then
  echo "✓ DCA Model Gateway Connector already present in this tenant"
else
  az ad sp create --id "$CONNECTOR_APP_ID" --query displayName -o tsv >/dev/null
  echo "✓ DCA Model Gateway Connector added to this tenant"
fi

SUB=$(az account show --query id -o tsv)
if [ "$ROLE" = "DCA Model Gateway Inference" ] && [ -z "$(az role definition list --custom-role-only true --name "$ROLE" --scope "/subscriptions/$SUB" --query "[0].name" -o tsv)" ]; then
  sed "s#/subscriptions/<your-subscription-id>#/subscriptions/$SUB#" "$HERE/dca-model-gateway-inference-role.json" > "${TMPDIR:-/tmp}/dca-model-gateway-role.json"
  az role definition create --role-definition @"${TMPDIR:-/tmp}/dca-model-gateway-role.json" -o none
  echo "✓ custom role \"$ROLE\" created in subscription $SUB"
fi

SCOPE=$(az resource show -g "$RG" -n "$NAME" --resource-type Microsoft.CognitiveServices/accounts --query id -o tsv)
for attempt in 1 2 3 4 5 6; do   # a role created seconds ago can take a moment to become assignable
  if az role assignment create --assignee "$CONNECTOR_APP_ID" --role "$ROLE" --scope "$SCOPE" -o none 2>/dev/null; then break; fi
  [ "$attempt" = 6 ] && { echo "✗ could not assign \"$ROLE\" on $SCOPE" >&2; exit 1; }
  sleep 20
done
ENDPOINT=$(az resource show --ids "$SCOPE" --query properties.endpoint -o tsv)
echo "✓ \"$ROLE\" assigned on $SCOPE"
echo "Next: on https://saas.dcassociatesgroup.com open Subscriptions, the subscription's menu, Connect your Foundry; enter"
echo "      $ENDPOINT"
echo "      and your deployment names, then select Save and test. Role assignments can take up to 10 minutes to apply."
