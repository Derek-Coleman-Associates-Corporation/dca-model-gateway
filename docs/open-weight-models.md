# Open-weight models and verified support

Updated November 12, 2026. DCAI Model Gateway is a routing service. Your provider must offer or host the model, grant the required inference permission, and expose an API operation the Gateway supports. A catalog entry or billing-tier match is not a successful compatibility test or a commercial-use license.

## Verified in live Gateway QA

These checks used DCAI's internal test deployment, synthetic prompts and no customer data. Marketplace Starter, Team and Partner subscriptions use the customer's connected provider instead; these internal deployments are not included inference credits.

| Model / path | Result | Boundary / limitation |
|---|---|---|
| Llama-4-Maverick | Three deterministic quality checks passed: arithmetic, JSON extraction and grounded unknown-answer handling; separate streaming check passed | Global `oss-only` route; no US twin configured in the internal test deployment |
| DeepSeek-V4-Pro | Three deterministic quality checks passed; response token totals reconciled | Global explicit-deployment path |
| DeepSeek-V4-Pro-dz | Successful US-route requests passed quality/token checks; a burst hit `429 RateLimitReached` with `Retry-After` | US data zone; provider capacity can be lower than Gateway plan limits; a later isolated retry passed after cooldown; pace requests and back off |
| gpt-oss-120b through provider model-router | Observed answering the arithmetic task correctly | Indirect selection only; `auto` can choose a frontier model on another request and is not an open-weight guarantee |

The small sample demonstrates working request paths, not a model leaderboard, comprehensive accuracy assessment, throughput guarantee or SLA. Raw evidence and the evaluation harness are in the private production repository; see the [customer-facing QA summary](qa-2026-11-12.md).

## Bring your own open-weight deployment

For Microsoft Foundry, the Gateway's customer path accepts a deployment name from a connected resource rather than a fixed product-wide model allowlist. Deploy a compatible model, connect the resource, map it to `oss-only` and use **Save and test**. The connection test must confirm the deployment before you rely on its billing tier. An arbitrary alias alone is not proof of model family.

For Google Vertex AI, configure its supported publisher/model identifier and location using the [Vertex guide](connect-your-vertex-ai.md). Vertex Responses API requests are not supported. Endpoint compatibility, regional availability, context length, streaming, tools and structured output depend on the specific model/version and provider.

| Family recognized by the current billing classifier | Customer setup / qualification |
|---|---|
| Llama | Compatible Foundry deployment or supported Vertex publisher model; review Meta's version-specific terms |
| DeepSeek | Compatible deployment/publisher model; verify version, quota and processing boundary |
| gpt-oss | Compatible deployment/publisher model; distinct from proprietary GPT models |
| Mistral, Mixtral, Ministral, Codestral | Verify the exact model's rights; family-name recognition does not mean unrestricted commercial use |
| Phi | Compatible deployment; validate the returned model identifier and operation |
| Qwen | Compatible deployment/publisher model; model/version licenses and regional catalog differ |
| Gemma | Supported provider deployment; review applicable terms and operation compatibility |
| Kimi | Supported provider deployment/publisher model; validate version and license |
| GLM | Supported provider deployment/publisher model; validate version and license |

Unknown or unconfirmed deployments can be charged at the frontier routing rate. The `oss-only` route rejects an unconfirmed/frontier target; it does not silently fall back to a frontier model. See [limits and billing](limits-and-billing.md).

```bash
curl https://ai-gateway-east-us1.azure-api.net/gateway/openai/v1/chat/completions \
  -H "api-key: $DCA_GATEWAY_KEY" \
  -H 'Content-Type: application/json' \
  -H 'x-dca-route: oss-only' \
  -d '{"messages":[{"role":"user","content":"What is 6 times 7? Reply with only the integer."}],"max_completion_tokens":128}'
```

This sends to your mapped deployment. A missing provider connection returns `409`; an unsuitable open-weight mapping returns `422`. Keep keys on the server. Respect `Retry-After` on `429`; use bounded exponential backoff with jitter, limit concurrent requests and avoid infinite retries. A calendar-month budget rejection (`403`) needs a budget/period resolution, not repeated requests.

## Expansion policy and limits

The Foundry catalog audit found additional candidates including Phi-4, Qwen3-32B, gpt-oss-20b/120b, Llama variants, Mistral variants and Kimi. They are **candidates for qualification**, not additional models proven live by this release. Catalog inclusion does not mean a model has been deployed, has available quota, or works with every endpoint.

To qualify a model: pin its provider/model/version and license; deploy in the required region; verify chat and any required streaming/tool/embedding operations; test refusal and timeout behavior; reconcile token usage; test routing and boundary controls; record measured latency and task quality. Add it to the verified table only when evidence passes. Do not advertise support for “all open-weight models” without these qualifications.

Self-hosted Ollama/vLLM servers, arbitrary third-party URLs, image/video generation and reranking are not exposed by the current customer connector. They need separate adapters and authentication, isolation and metering work. Opening an arbitrary URL input is not an acceptable substitute.

Provider catalogs: [Microsoft Foundry models](https://azure.microsoft.com/en-us/products/ai-foundry/models/) and [Vertex Model Garden](https://cloud.google.com/vertex-ai/generative-ai/docs/model-garden/explore-models). Example publisher model cards: [Phi-4 — MIT](https://huggingface.co/microsoft/phi-4), [Qwen3-32B — Apache 2.0](https://huggingface.co/Qwen/Qwen3-32B), [gpt-oss-120b — Apache 2.0](https://huggingface.co/openai/gpt-oss-120b). These examples do not establish the licenses of every family member or replace provider terms.
