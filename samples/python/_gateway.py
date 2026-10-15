"""Shared settings for the samples. Set DCA_GATEWAY_KEY (your gateway key) before running; never hard-code it."""
import os
import sys

GATEWAY_URL = os.environ.get("DCA_GATEWAY_URL", "https://ai-gateway-east-us1.azure-api.net/gateway").rstrip("/")
KEY = os.environ.get("DCA_GATEWAY_KEY")
# The name of a deployment in YOUR Azure AI Foundry resource (for example "gpt-4.1-mini").
DEPLOYMENT = os.environ.get("DCA_DEPLOYMENT", "gpt-4.1-mini")

if not KEY:
    sys.exit("Set DCA_GATEWAY_KEY to your gateway key (Subscriptions page -> Regenerate gateway key).")
