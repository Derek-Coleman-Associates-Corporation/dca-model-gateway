"""The OpenAI Responses API through the gateway (/openai/v1/responses)."""
from openai import OpenAI

from _gateway import DEPLOYMENT, GATEWAY_URL, KEY

client = OpenAI(base_url=f"{GATEWAY_URL}/openai/v1", api_key=KEY, default_headers={"api-key": KEY})

response = client.responses.create(model=DEPLOYMENT, input="Give one word that rhymes with gateway.", max_output_tokens=16)
print(response.output_text, "|", response.model)
