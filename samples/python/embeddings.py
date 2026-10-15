"""Embeddings through the gateway. Uses the deployment you mapped to the embeddings route, else the one you name here."""
import os

from openai import OpenAI

from _gateway import GATEWAY_URL, KEY

EMBEDDING_DEPLOYMENT = os.environ.get("DCA_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")

client = OpenAI(base_url=f"{GATEWAY_URL}/openai/v1", api_key=KEY, default_headers={"api-key": KEY})

result = client.embeddings.create(model=EMBEDDING_DEPLOYMENT, input=["DCA Model Gateway", "API gateway"])
print(len(result.data), "vectors of", len(result.data[0].embedding), "dimensions |", result.model)
