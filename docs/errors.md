# Errors

Every error the gateway itself returns is JSON with an `error.code`. When the gateway refuses a request, it was **not
forwarded** to any model. The Anthropic API wraps the same codes in Anthropic's error shape
(`{"type":"error","error":{…}}`).

## From the gateway

| Status | `error.code` / message | Meaning | What to do |
|---|---|---|---|
| 401 | `Access denied due to missing subscription key` | No key in the request | Send `api-key` (OpenAI APIs) or `x-api-key` (Anthropic API) |
| 401 | `Access denied due to invalid subscription key` | Wrong key, a rotated or revoked key, or a cancelled subscription | Use the current key; regenerate it on the Subscriptions or Tenant keys page if needed |
| 400 | `invalid_data_boundary` | `x-dca-data-boundary` is not `any` or `us` | Fix the header |
| 409 | `foundry_not_connected` | This subscription has no Foundry connected, or it was disconnected | [Connect your Foundry](connect-your-foundry.md) |
| 422 | `route_not_configured` | The route has no deployment and no fallback (for example `oss-only`), or nothing names a deployment | Map the route on the Connect your Foundry page, or name a deployment in `model` |
| 422 | `no_eligible_provider` | `x-dca-data-boundary: us`, and no deployment is declared for the United States boundary for this request | Declare a US deployment in the third column, or drop the header |
| 429 | (rate limit) | This key used its tokens-per-minute allowance | Wait `retry-after` seconds; see [Limits](limits-and-billing.md) |
| 403 | (quota) | This key used its monthly token cap, or the monthly budget you set for it on the Tenant keys page | Resets on the 1st of the month (UTC). Raise or remove the key's budget on [Tenant keys](tenant-keys.md), or contact support to discuss a larger plan |
| 502 | `foundry_auth_failed` + `aadsts` | Your Microsoft Entra tenant refused to issue the connector a token | See the table below |
| 502 | `byo_config_invalid` | The saved connection is incomplete | Open Connect your Foundry and select **Save and test** again |
| 502 | `vertex_auth_failed` + `google` | Google refused the workload identity federation exchange for your Vertex AI project | See [Connect your Vertex AI](connect-your-vertex-ai.md#errors-you-may-see) |
| 422 | `not_supported_by_provider` | Responses API or the Anthropic API on a Google Vertex AI connection | Use chat completions |
| 400 | `invalid_input` | Embeddings on a Google Vertex AI connection with input that is not text (token arrays) | Send a string or a list of up to 250 strings |
| 503 | `byo_config_unavailable`, `gateway_identity_unavailable` | A temporary problem on our side | Retry with backoff; if it persists, contact support |

### `foundry_auth_failed`: the `aadsts` code

| `aadsts` | Cause | Fix |
|---|---|---|
| `AADSTS700016` | The DCA Model Gateway Connector is not in your tenant | Step 1 of [Connect your Foundry](connect-your-foundry.md): admin consent, or `az ad sp create --id 7154fd27-4506-4cd5-8e3a-b2e5208d0846` |
| `AADSTS7000112` | The connector's enterprise application is disabled in your tenant | Enable it in Microsoft Entra ID, Enterprise applications |
| `AADSTS53003` | A Conditional Access policy blocked the connector | Exclude the connector's service principal from workload-identity Conditional Access |
| `AADSTS90002` | The tenant was not found | Contact support |
| other | Microsoft Entra refused the request | Contact support with the code and the time of the request |

## From your Foundry (passed through)

When the gateway reached your resource, your resource's own answer is returned unchanged. The response still carries
`x-dca-backend: customer-foundry`.

| Status | Typical `error.code` | Meaning | What to do |
|---|---|---|---|
| 401 | `PermissionDenied` | The connector has no role on this resource, or the assignment has not applied yet | Step 2 of [Connect your Foundry](connect-your-foundry.md); allow up to 10 minutes |
| 400 | `Tenant provided in token does not match resource token` | The resource belongs to a different Microsoft Entra tenant than the one that owns your subscription | Connect a resource in your own tenant. The gateway always signs in to the tenant that bought the subscription |
| 403 | | Your resource's network rules block public traffic | Allow public network access on the resource |
| 404 | `DeploymentNotFound` | No deployment with that name | Check the name in `model` or in your mapping |
| 429 | | Your deployment's own quota (tokens or requests per minute) | Wait `retry-after`, or raise the deployment's quota in Azure |
| 400 | `content_filter`, `invalid_request_error`, … | Your deployment rejected the request | As for a direct call to your deployment |
