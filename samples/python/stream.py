"""Streaming chat completion (server-sent events pass straight through the gateway)."""
from openai import OpenAI

from _gateway import DEPLOYMENT, GATEWAY_URL, KEY

client = OpenAI(base_url=f"{GATEWAY_URL}/openai/v1", api_key=KEY, default_headers={"api-key": KEY})

stream = client.chat.completions.create(
    model=DEPLOYMENT,
    messages=[{"role": "user", "content": "Count from 1 to 5, separated by spaces."}],
    max_completion_tokens=40,
    stream=True,
)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
