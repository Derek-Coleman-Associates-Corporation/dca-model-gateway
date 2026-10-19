# Connect your Google Vertex AI

DCA Model Gateway can send requests to **Gemini and the other models you use in Google Vertex AI**, in your own Google
Cloud project. No key is created or shared. Your own Microsoft Entra tenant issues a short-lived token to the DCA Model
Gateway Connector; the gateway exchanges it at Google for a short-lived token of a workload identity pool that you control,
and Vertex AI checks your IAM policy on every call. Your provider trusts only tokens from **your** tenant, so no other
organization's connection can reach your project, even one that names your project, pool and provider.

Your project's model usage is billed by Google on your own billing account. DCA Model Gateway bills its plan and routed
tokens through Microsoft Marketplace, the same as with an Azure AI Foundry connection.

## What works today

| Gateway API | With Vertex AI |
|---|---|
| Chat completions (`/openai/v1/chat/completions`, also the legacy `/openai/deployments/{name}/chat/completions`) | ✅ Gemini and the open-weight models on Vertex AI's OpenAI-compatible endpoint, streaming included |
| Open-weight models (Model Garden managed APIs, ids ending in `-maas`) | ✅ for example `openai/gpt-oss-120b-maas`, `deepseek-ai/deepseek-v3.2-maas`, `qwen/qwen3-235b-a22b-instruct-2507-maas`, `zai-org/glm-4.7-maas`; billed on the open-weight tier |
| Embeddings (`/openai/v1/embeddings`) | ✅ OpenAI format in and out; the gateway calls Vertex AI's native API (input: a string or up to 250 strings, optional `dimensions`) |
| Routes (`x-dca-route`) and the United States data boundary (`x-dca-data-boundary: us`) | ✅ |
| Tenant keys, per-key budgets, usage view and CSV export | ✅ |
| Responses API | ❌ refused with `422 not_supported_by_provider`, never forwarded |
| Anthropic Messages API | ⏳ not supported yet (Claude through Vertex AI is in testing). Without a mapped Claude model a request is refused with `422 route_not_configured` |

## Step 1: add the connector to your tenant

Google will trust only tokens that your Microsoft Entra tenant issues to the **DCA Model Gateway Connector**, so the
connector must exist in your tenant. It holds no secrets: only DCA Model Gateway can act as it. This needs an administrator
who may add enterprise applications (Global Administrator, Application Administrator or Cloud Application Administrator).

- **Admin consent link.** On the portal's **Connect your Foundry** page, **Google Vertex AI** tab, select **Grant admin
  consent** and accept for your organization. You come back to the page with a confirmation.
- **Azure CLI** (for example in Azure Cloud Shell):

  ```bash
  az ad sp create --id 7154fd27-4506-4cd5-8e3a-b2e5208d0846
  ```

If you already connected an Azure AI Foundry, the connector is in your tenant already.

## Step 2: let the connector call Vertex AI in your project

Run once, as someone who can manage IAM in the project (Owner, or Role Administrator, Workload Identity Pool Admin and
Project IAM Admin), for example in Cloud Shell. `TENANT_ID` is your Microsoft Entra tenant: the tenant of the Marketplace
subscription, shown on the portal's Connect page. The last two commands grant a custom role with one permission,
`aiplatform.endpoints.predict`: the gateway can call models and nothing else.

```bash
PROJECT_ID=your-project-id
TENANT_ID=your-entra-tenant-id
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud services enable aiplatform.googleapis.com sts.googleapis.com iamcredentials.googleapis.com --project $PROJECT_ID
gcloud iam workload-identity-pools create dca-model-gateway --project $PROJECT_ID --location global \
  --display-name "DCA Model Gateway"
gcloud iam workload-identity-pools providers create-oidc dca-gateway --project $PROJECT_ID --location global \
  --workload-identity-pool dca-model-gateway \
  --issuer-uri "https://sts.windows.net/$TENANT_ID/" \
  --allowed-audiences "api://7154fd27-4506-4cd5-8e3a-b2e5208d0846" \
  --attribute-mapping "google.subject=assertion.appid" \
  --attribute-condition "assertion.appid == '7154fd27-4506-4cd5-8e3a-b2e5208d0846' && assertion.tid == '$TENANT_ID'"
gcloud iam roles create dcaModelGatewayInference --project $PROJECT_ID --title "DCA Model Gateway Inference" \
  --permissions aiplatform.endpoints.predict --stage GA
gcloud projects add-iam-policy-binding $PROJECT_ID --role projects/$PROJECT_ID/roles/dcaModelGatewayInference \
  --member "principal://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/dca-model-gateway/subject/7154fd27-4506-4cd5-8e3a-b2e5208d0846"
```

The built-in **Vertex AI User** role (`roles/aiplatform.user`) also works, but it allows much more than calling models.

What these values are:

| Value | Meaning |
|---|---|
| `https://sts.windows.net/<your tenant>/` | Your own Microsoft Entra tenant, which issues the connector's token. The gateway asks only the tenant of your Marketplace subscription, taken from your sign-in; it is never typed in |
| `api://7154fd27-…` | The token's audience: the DCA Model Gateway Connector application |
| `7154fd27-…` (subject) | The connector's application ID. With the issuer, the provider accepts **only** tokens your tenant issues to the connector |

Gemini and the managed open-weight models (ids ending in `-maas`, such as the ones listed above) work as soon as the Vertex AI
API is enabled. Llama needs its license accepted in Model Garden first; Mistral models use a different Vertex AI API that the
gateway does not call yet. Not every model is offered in every location: the open-weight models above are offered in `global`;
Llama 4 Maverick only in `us-east5`. For the United States boundary, `openai/gpt-oss-120b-maas` is offered in `us-central1`
and the Qwen3 model in `us-south1`, not in the `us` multi-region that newer Gemini models need. A route can therefore name its
own location (see step 3). If your
organization restricts workload identity providers (`constraints/iam.workloadIdentityPoolProviders`), allow the issuer
`https://sts.windows.net/<your tenant>/`.

### Set up before October 18, 2026?

Earlier versions of this guide had the provider trust DCA's tenant and the gateway's managed identity. The gateway no
longer presents that token, so that setup no longer works for anyone. Update the provider and the role binding:

```bash
gcloud iam workload-identity-pools providers update-oidc dca-gateway --project $PROJECT_ID --location global \
  --workload-identity-pool dca-model-gateway --issuer-uri "https://sts.windows.net/$TENANT_ID/" \
  --attribute-mapping "google.subject=assertion.appid" \
  --attribute-condition "assertion.appid == '7154fd27-4506-4cd5-8e3a-b2e5208d0846' && assertion.tid == '$TENANT_ID'"
gcloud projects add-iam-policy-binding $PROJECT_ID --role projects/$PROJECT_ID/roles/dcaModelGatewayInference \
  --member "principal://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/dca-model-gateway/subject/7154fd27-4506-4cd5-8e3a-b2e5208d0846"
gcloud projects remove-iam-policy-binding $PROJECT_ID --role projects/$PROJECT_ID/roles/dcaModelGatewayInference \
  --member "principal://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/dca-model-gateway/subject/d1567b77-2a75-49a5-9c0b-2593c8a6488a"
```

## Step 3: connect it on the portal

1. Open [saas.dcassociatesgroup.com](https://saas.dcassociatesgroup.com), **Subscriptions**, the subscription's menu,
   **Connect your Foundry**, then the **Google Vertex AI** tab.
2. Enter the project ID and project number. Keep the pool and provider IDs from step 2 (`dca-model-gateway`, `dca-gateway`).
3. **Location**: `global` (Google may process the request in any location), the `us` or `eu` multi-region, or a region.
   **United States location** (optional): `us` or a US region, used for requests with `x-dca-data-boundary: us`. Newer
   Gemini models are offered in `global` and the multi-regions, not in single regions.
4. Map at least the default route to a Vertex AI model id, for example `google/gemini-3.8-flash`. A bare Gemini name gets
   `google/` added. A model offered only in a region can carry its own location, `location:publisher/model`: for example
   `us-east5:meta/llama-4-maverick-17b-128e-instruct-maas` on the `oss-only` route goes to us-east5 while the other routes stay
   in the connection's location. In the column for the United States boundary, only United States locations are accepted
   (`us-central1:openai/gpt-oss-120b-maas`), and a request is never sent outside the United States. Map **embeddings** to an embedding model such as `google/gemini-embedding-001` (offered in `global` and
   single regions, not in the `us`/`eu` multi-regions: for embeddings under the United States boundary, use a US region
   such as `us-central1` as the United States location). Models for the United States boundary go in the last column.
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
  about five minutes.
- **In your Microsoft Entra tenant**: disabling or deleting the DCA Model Gateway Connector's enterprise application also
  stops new token exchanges, within about five minutes. With `x-dca-data-boundary: us`, a connection without a United States location is refused, never sent
  to the global endpoint.

## Errors you may see

| Status | `error.code` | Meaning | Fix |
|---|---|---|---|
| 502 | `foundry_auth_failed` | Your Microsoft Entra tenant did not issue the connector's token. The `aadsts` field holds the code, for example `AADSTS700016` (the connector is not in your tenant) | Step 1 |
| 502 | `vertex_auth_failed` | Google refused the token exchange. The `google` field holds Google's code, for example `invalid_target` (pool or provider not found), `invalid_grant` (issuer or audience) or `unauthorized_client` (attribute condition) | Check step 2: project number, pool and provider IDs, the issuer (your tenant), audience and attribute condition |
| 403 | `PERMISSION_DENIED` (from Vertex AI) | The pool principal has no Vertex AI role, or the API is disabled | The role binding in step 2; allow a few minutes after a change |
| 404 | (from Vertex AI) | The model is not available in that location, or not enabled in your project | Use a model id your project can call, in a location that offers it |
| 422 | `not_supported_by_provider` | Responses API on a Vertex AI connection | Use chat completions |
| 400 | `invalid_input` | Embeddings input that is not a string or a list of 1 to 250 strings (token arrays are not supported) | Send text |
| 422 | `no_eligible_provider` | `x-dca-data-boundary: us` and no model is declared for the United States boundary | Fill the last column, and set a United States location |
| 422 | `route_not_configured` | The route you asked for (for example `oss-only`) is not mapped. `oss-only` never falls back to the default model | Map the route on the Connect page |
