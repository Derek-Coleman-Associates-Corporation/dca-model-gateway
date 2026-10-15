"""Existing Azure OpenAI code works unchanged: point azure_endpoint at the gateway and use the gateway key.
The legacy /openai/deployments/{deployment}/... path is translated to your deployment by the gateway."""
from openai import AzureOpenAI

from _gateway import DEPLOYMENT, GATEWAY_URL, KEY

client = AzureOpenAI(azure_endpoint=GATEWAY_URL, api_key=KEY, api_version="2024-10-21")

completion = client.chat.completions.create(
    model=DEPLOYMENT,  # with AzureOpenAI, `model` is the deployment name
    messages=[{"role": "user", "content": "Reply with the single word OK"}],
    max_completion_tokens=8,
)
print(completion.choices[0].message.content, "|", completion.model)
