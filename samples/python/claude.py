"""Claude through the gateway with the official Anthropic Python SDK (Anthropic Messages API).
The gateway uses the Claude deployment you mapped on the Connect your Foundry page, else the deployment named in `model`."""
import os

import anthropic

from _gateway import GATEWAY_URL, KEY

CLAUDE_DEPLOYMENT = os.environ.get("DCA_CLAUDE_DEPLOYMENT", "claude-sonnet-4-6")

client = anthropic.Anthropic(base_url=f"{GATEWAY_URL}/anthropic", api_key=KEY)  # sent as x-api-key

message = client.messages.create(
    model=CLAUDE_DEPLOYMENT,
    max_tokens=64,
    messages=[{"role": "user", "content": "In one sentence, what does a model gateway do?"}],
)
print(message.content[0].text, "|", message.model)
