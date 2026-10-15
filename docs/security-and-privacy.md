# Security and privacy

## What the gateway can reach

- **Only what you grant.** The gateway calls your Foundry as the *DCA Model Gateway Connector*, using a Microsoft Entra token
  that your tenant issues. The connector has no secrets. Only the gateway's own Azure managed identity can act as it.
- **The tenant is fixed.** A connection always uses the Microsoft Entra tenant that owns the subscription, taken from your
  sign-in, never typed in. A token issued by your tenant cannot open another organization's resources, and theirs cannot
  open yours.
- **Stop at any time.** **Disconnect** on the Connect your Foundry page stops the gateway immediately. Removing the
  connector's role assignment, or its enterprise application, blocks it in Azure too, once Azure applies the change; that
  can take several minutes or longer.

### Which role to grant

| Role | What it allows | |
|---|---|---|
| **DCA Model Gateway Inference** (custom, [definition](../samples/connect/dca-model-gateway-inference-role.json)) | Data-plane calls to your deployments only. No keys, no connection secrets, no access to the resource's settings. | Recommended |
| **Cognitive Services User** (built-in) | The same data-plane calls, **plus** listing the resource's keys and reading its settings | Simpler to assign; broader than the gateway needs |

The gateway never lists keys or reads settings with either role. The custom role makes that a guarantee rather than a
promise. Creating it needs permission to create custom roles in your Azure subscription, such as Owner or User Access
Administrator. See [Connect your Foundry](connect-your-foundry.md#step-2-give-the-connector-a-role-on-your-resource).

## What the gateway stores

| Data | Where | Kept |
|---|---|---|
| Your connection: tenant ID, endpoint, deployment names, last test result | Azure Storage, East US, encrypted at rest, Entra-only access | While the subscription is active; deleted within an hour of cancellation |
| Per-request telemetry: key ID, route, deployment name, data boundary, token counts, time | Azure Monitor, United States | 90 days |
| Usage reported to Microsoft Marketplace for billing | Microsoft Marketplace, plus our billing audit records | As required for invoicing and audit |
| Account records: subscription and plan, the signed-in user's name, e-mail address and Microsoft Entra IDs, consent records | Azure SQL, United States | See the privacy notice |

**Not stored:** prompts, responses, files, embeddings vectors, and Foundry keys. The gateway logs no request or response
bodies, and caches none for connected Foundry deployments.

## Where requests go

Your request travels over TLS to the gateway (Azure API Management, East US), then over TLS to your Foundry endpoint. Model
inference runs in your deployment, in the region or data zone of that deployment's type. Use `x-dca-data-boundary: us`
together with US data-zone deployments to keep processing in the United States; see
[Data boundary](api-reference.md#data-boundary).

## Your gateway key

- Treat it like a password. Store it in a secret manager and never put it in client-side code.
- If it leaks, choose **Regenerate gateway key**. The old key stops working immediately.
- Support never asks for your key. Send your Marketplace subscription ID instead.

## More

- Privacy notice: <https://www.dcassociatesgroup.com/privacy>
- Reporting a vulnerability: [SECURITY.md](../SECURITY.md)
