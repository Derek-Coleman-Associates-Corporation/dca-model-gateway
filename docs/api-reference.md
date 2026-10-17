# API reference

## Base URL and authentication

| API | Base URL | Key header |
|---|---|---|
| OpenAI v1 and Azure OpenAI | `https://ai-gateway-east-us1.azure-api.net/gateway` | `api-key: <gateway key>` |
| Anthropic Messages | `https://ai-gateway-east-us1.azure-api.net/gateway/anthropic` | `x-api-key: <gateway key>` |

Keep the key in a header. The gateway also accepts it as the `subscription-key` query parameter (it removes the key before
forwarding the request and hides it in its own logs), but URLs tend to end up in logs on your side, such as proxies and
browser history. The OpenAI SDKs send their `api_key` as `Authorization: Bearer`, so add `default_headers={"api-key": key}` as the
samples do. The Azure OpenAI and Anthropic SDKs already use the right header.

## Endpoints

| Method and path | Speaks | Notes |
|---|---|---|
| `POST /openai/v1/chat/completions` | OpenAI Chat Completions | Streaming supported |
| `POST /openai/v1/responses` | OpenAI Responses | |
| `POST /openai/v1/embeddings` | OpenAI Embeddings | |
| `POST /openai/deployments/{deployment}/chat/completions?api-version=…` | Azure OpenAI | For the Azure OpenAI SDKs; translated to the v1 call above |
| `POST /openai/deployments/{deployment}/embeddings?api-version=…` | Azure OpenAI | Same |
| `POST /anthropic/v1/messages` | Anthropic Messages | Streaming supported |
| `POST /anthropic/v1/messages/count_tokens` | Anthropic token counting | |

Request and response bodies are those of the API you call; the gateway passes them through. It changes only the `model`
field, to the deployment it chose.

## How the gateway chooses a deployment

For the OpenAI-compatible endpoints, in this order:

1. **`x-dca-route` header present**: the deployment you mapped to that route on the
   [Connect your Foundry](connect-your-foundry.md) page. The request's `model` is ignored. An unmapped route uses your default
   deployment, except `oss-only`, which is refused.
2. **No route, `model` names a deployment**: that deployment of your resource. Any deployment of the connected resource can
   be named.
3. **No route, no `model`**: your default deployment.

Embeddings use the deployment mapped to *embeddings*, else the one named in `model`. The Anthropic API uses the deployment
mapped to *Claude*, else the one named in `model`.

## Routes

| `x-dca-route` | Intended for | If you did not map it |
|---|---|---|
| `cheap` | Lowest-cost deployment, for example an open-weight model | Default deployment |
| `oss-only` | Open-weight models only | `422 route_not_configured`; never sent to the default |
| `auto` | A model-router deployment that picks per request | Default deployment |
| `reasoning` | A reasoning model | Default deployment |
| `code` | A coding model | Default deployment |
| `frontier` | Your most capable model | Default deployment |
| `passthrough` or no header | Use `model`, else the default | |

## Data boundary

| `x-dca-data-boundary` | Behaviour |
|---|---|
| `any` (default) | Uses the deployments in your main mapping. Where inference runs depends on each deployment's type (Global, Data Zone or regional). |
| `us` | Uses **only** the deployments you declared for the United States data boundary. A request with no declared deployment is refused with `422 no_eligible_provider` and is never rerouted. |
| anything else | `400 invalid_data_boundary` |

The gateway enforces your declaration. It cannot see your deployments' types, so declare only US data-zone or US regional
deployments.

## Request headers

| Header | Values | |
|---|---|---|
| `api-key` / `x-api-key` | Your gateway key | Required |
| `x-dca-route` | See [Routes](#routes) | Optional |
| `x-dca-data-boundary` | `any`, `us` | Optional |

## Response headers

| Header | Example | Meaning |
|---|---|---|
| `x-dca-backend` | `customer-foundry` | Your own Foundry served the request |
| `x-dca-model` | `gpt-4.1-mini` | The deployment the gateway called |
| `x-dca-data-boundary` | `any` | The boundary applied |
| `x-dca-processing-scope` | `customer-deployment` | Processing happened in your deployment, under its own region or data zone |
| `x-dca-remaining-tokens` | `59870` | Tokens left in the current minute for this key |
| `x-dca-remaining-quota-tokens` | `499999824` | Tokens left this calendar month for this key |
| `x-dca-budget-remaining-tokens` | `99999976` | Tokens left this calendar month in the budget you set for this key (only on keys with a budget) |
| `x-dca-tokens-consumed` | `24` | Prompt and completion tokens of this request |
| `retry-after` | `12` | Seconds to wait, on `429` and `403` limit responses |

Your deployment's own headers, for example its rate-limit headers, pass through as well.

## Streaming

`"stream": true` works on chat completions and the Anthropic Messages API; events pass through as they arrive. With the
OpenAI API, add `"stream_options": {"include_usage": true}` if your application needs the usage totals in the stream.

## Compatibility notes

- **OpenAI SDKs**: set the base URL to `…/gateway/openai/v1` and add the `api-key` default header.
- **Azure OpenAI SDKs**: set the endpoint to `…/gateway`; `model` is your deployment name. Use API version `2024-10-21` or later.
- **Anthropic SDKs**: set the base URL to `…/gateway/anthropic`. The `anthropic-version` header defaults to `2023-06-01` if you omit it.
- **Timeouts**: the gateway forwards while your deployment generates. Use your SDK's normal timeouts for long generations.
