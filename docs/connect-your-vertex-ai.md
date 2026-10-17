# Connect your Google Vertex AI

DCA Model Gateway can send requests to **Gemini and the other models you use in Google Vertex AI**, in your own Google
Cloud project. No key is created or shared: the gateway exchanges its own Microsoft Entra managed-identity token at Google
for a short-lived token of a workload identity pool that you control, and Vertex AI checks your IAM policy on every call.

Your project's model usage is billed by Google on your own billing account. DCA Model Gateway bills its plan and routed
tokens through Microsoft Marketplace, the same as with an Azure AI Foundry connection.

## What works today

| Gateway API | With Vertex AI |
|---|---|
| Chat completions (`/openai/v1/chat/completions`, also the legacy `/openai/deployments/{name}/chat/completions`) | ✅ Gemini and the other models on Vertex AI's OpenAI-compatible endpoint, streaming included |
| Routes (`x-dca-route`) and the United States data boundary (`x-dca-data-boundary: us`) | ✅ |
| Tenant keys, per-key budgets, usage view and CSV export | ✅ |
| Responses API, embeddings, Anthropic Messages API | ❌ refused with `422 not_supported_by_provider`, never forwarded |

## Step 1: let the gateway call Vertex AI in your project

Run once, as someone who can manage IAM in the project (Owner, or Role Administrator, Workload Identity Pool Admin and
Project IAM Admin), for example in Cloud Shell. The last two commands grant a custom role with one permission,
`aiplatform.endpoints.predict`: the gateway can call models and nothing else.

```bash
PROJECT_ID=your-project-id
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud services enable aiplatform.googleapis.com sts.googleapis.com iamcredentials.googleapis.com --project $PROJECT_ID
gcloud iam workload-identity-pools create dca-model-gateway --project $PROJECT_ID --location global \
  --display-name "DCA Model Gateway"
gcloud iam workload-identity-pools providers create-oidc dca-gateway --project $PROJECT_ID --location global \
  --workload-identity-pool dca-model-gateway \
  --issuer-uri "https://sts.windows.net/a42a9fb4-e76a-4b34-b070-3bf3687022f0/" \
  --allowed-audiences "api://7154fd27-4506-4cd5-8e3a-b2e5208d0846" \
  --attribute-mapping "google.subject=assertion.sub" \
  --attribute-condition "assertion.sub == 'd1567b77-2a75-49a5-9c0b-2593c8a6488a'"
gcloud iam roles create dcaModelGatewayInference --project $PROJECT_ID --title "DCA Model Gateway Inference" \
  --permissions aiplatform.endpoints.predict --stage GA
gcloud projects add-iam-policy-binding $PROJECT_ID --role projects/$PROJECT_ID/roles/dcaModelGatewayInference \
  --member "principal://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/dca-model-gateway/subject/d1567b77-2a75-49a5-9c0b-2593c8a6488a"
```

The built-in **Vertex AI User** role (`roles/aiplatform.user`) also works, but it allows much more than calling models.

What these values are:

| Value | Meaning |
|---|---|
| `https://sts.windows.net/a42a9fb4-…/` | The Microsoft Entra tenant of Derek Coleman & Associates, which issues the gateway's token |
| `api://7154fd27-…` | The token's audience: the DCA Model Gateway Connector application |
| `d1567b77-…` | The gateway's managed identity. The attribute condition makes the provider accept **only** this identity |

Gemini models work as soon as the Vertex AI API is enabled. Other Model Garden models (for example Llama or Claude) must be
enabled in your project first; Mistral models use a different Vertex AI API that the gateway does not call yet. If your
organization restricts workload identity providers (`constraints/iam.workloadIdentityPoolProviders`), allow the issuer
above.

## Step 2: connect it on the portal

1. Open [saas.dcassociatesgroup.com](https://saas.dcassociatesgroup.com), **Subscriptions**, the subscription's menu,
   **Connect your Foundry**, then the **Google Vertex AI** tab.
2. Enter the project ID and project number. Keep the pool and provider IDs from step 1 (`dca-model-gateway`, `dca-gateway`).
3. **Location**: `global` (Google may process the request in any location), the `us` or `eu` multi-region, or a region.
   **United States location** (optional): `us` or a US region, used for requests with `x-dca-data-boundary: us`. Newer
   Gemini models are offered in `global` and the multi-regions, not in single regions.
4. Map at least the default route to a Vertex AI model id, for example `google/gemini-3.8-flash`. A bare Gemini name gets
   `google/` added. Models for the United States boundary go in the last column.
5. Select **Save and test**. Every mapped route is called once through the gateway with your own key.

## Use it

Nothing changes in your applications: call `https://ai-gateway-east-us1.azure-api.net/gateway/openai/v1` with your gateway
key, as in [Getting started](getting-started.md). Name a model (`"model": "google/gemini-3.8-flash"`), or pick a route with
`x-dca-route`. Responses carry `x-dca-backend: customer-vertex`.

Gemini's "thinking" tokens are part of the token count Google reports, so they count as routed tokens. Gemini models are
billed on the frontier tier; open models such as Gemma or Llama on the open-weight tier. See
[Limits and billing](limits-and-billing.md).

## Change, disconnect, revoke

- **Change**: edit the page and select **Save and test**. A connection is either Azure AI Foundry or Vertex AI; saving one
  replaces the other.
- **Disconnect** on the portal stops the gateway at once (`409 foundry_not_connected`); **Reconnect** resumes it.
- **In your project**: remove the role binding (in our tests the gateway was refused about a minute later; Google allows up
  to seven), or disable the pool. Disabling or deleting only the provider stops new token exchanges, but tokens already
  issued stay valid until they expire; the gateway exchanges again at least every five minutes, so it loses access within
  about five minutes. With `x-dca-data-boundary: us`, a connection without a United States location is refused, never sent
  to the global endpoint.

## Errors you may see

| Status | `error.code` | Meaning | Fix |
|---|---|---|---|
| 502 | `vertex_auth_failed` | Google refused the token exchange. The `google` field holds Google's code, for example `invalid_target` (pool or provider not found) or `invalid_grant` (audience or attribute condition) | Check step 1: project number, pool and provider IDs, allowed audience, attribute condition |
| 403 | `PERMISSION_DENIED` (from Vertex AI) | The pool principal has no Vertex AI role, or the API is disabled | The role binding in step 1; allow a few minutes after a change |
| 404 | (from Vertex AI) | The model is not available in that location, or not enabled in your project | Use a model id your project can call, in a location that offers it |
| 422 | `not_supported_by_provider` | Responses API, embeddings or the Anthropic API on a Vertex AI connection | Use chat completions |
| 422 | `no_eligible_provider` | `x-dca-data-boundary: us` and no model is declared for the United States boundary | Fill the last column, and set a United States location |
