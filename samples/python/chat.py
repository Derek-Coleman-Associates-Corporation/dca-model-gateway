"""Chat completion through DCA Model Gateway with the official OpenAI Python SDK."""
from openai import OpenAI

from _gateway import DEPLOYMENT, GATEWAY_URL, KEY

client = OpenAI(
    base_url=f"{GATEWAY_URL}/openai/v1",
    api_key=KEY,
    default_headers={"api-key": KEY},  # the gateway reads the key from the api-key header
)

# `model` names a deployment in your own Foundry. The gateway forwards the call to it.
response = client.chat.completions.with_raw_response.create(
    model=DEPLOYMENT,
    messages=[{"role": "user", "content": "In one sentence, what is an API gateway?"}],
    max_completion_tokens=60,
)
completion = response.parse()
print(completion.choices[0].message.content)
print("served by:", response.headers.get("x-dca-backend"), "| deployment:", response.headers.get("x-dca-model"),
      "| model:", completion.model, "| tokens left this month:", response.headers.get("x-dca-remaining-quota-tokens"))
