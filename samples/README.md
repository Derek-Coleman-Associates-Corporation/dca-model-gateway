# Samples

Every sample reads your key from the environment and was run against the live gateway before publication.

```bash
export DCA_GATEWAY_KEY="<your gateway key>"
export DCA_DEPLOYMENT="<a deployment in your Foundry, for example gpt-4.1-mini>"
```

| Sample | What it shows |
|---|---|
| [`python/chat.py`](python/chat.py) | Chat completion with the OpenAI SDK, and the gateway's response headers |
| [`python/routes.py`](python/routes.py) | `x-dca-route`: the gateway picks your mapped deployment |
| [`python/stream.py`](python/stream.py) | Streaming |
| [`python/azure_openai_sdk.py`](python/azure_openai_sdk.py) | Existing Azure OpenAI code, unchanged |
| [`python/responses_api.py`](python/responses_api.py) | The Responses API |
| [`python/embeddings.py`](python/embeddings.py) | Embeddings (`DCA_EMBEDDING_DEPLOYMENT`) |
| [`python/claude.py`](python/claude.py) | Claude with the Anthropic SDK (`DCA_CLAUDE_DEPLOYMENT`) |
| [`python/check_connection.py`](python/check_connection.py) | One request and a plain-language verdict, for troubleshooting |
| [`javascript/chat.mjs`](javascript/chat.mjs) | Chat completion with the OpenAI Node.js SDK |
| [`javascript/claude.mjs`](javascript/claude.mjs) | Claude with the Anthropic Node.js SDK |
| [`curl/chat.sh`](curl/chat.sh), [`curl/routes.sh`](curl/routes.sh), [`curl/us-boundary.sh`](curl/us-boundary.sh), [`curl/claude.sh`](curl/claude.sh) | The same with curl |
| [`connect/connect-foundry.sh`](connect/connect-foundry.sh) | One-time setup in your tenant: the connector and its role |

**Python**

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r samples/python/requirements.txt
python3 samples/python/chat.py
```

**Node.js** 18 or later

```bash
cd samples/javascript && npm install && node chat.mjs
```
