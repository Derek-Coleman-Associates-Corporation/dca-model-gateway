# Connect your Foundry

DCA Model Gateway calls **your** Azure AI Foundry deployments. You connect them once per subscription, in three steps. No
key is shared: the gateway signs in to your tenant as an application you control with Azure role-based access control.

## The DCA Model Gateway Connector

| | |
|---|---|
| Application (client) ID | `7154fd27-4506-4cd5-8e3a-b2e5208d0846` |
| Name in your tenant | DCA Model Gateway Connector |
| Credentials | None. It holds no secrets or certificates; only the gateway's own managed identity can act as it. |
| Microsoft Graph permission | *Sign in and read user profile*, delegated. Microsoft Entra requires at least one permission for tenant-wide consent; the connector never signs anyone in. |
| What it can reach | Only the Azure resources you assign it a role on |

## Requirements

- The Foundry resource is in the **same Microsoft Entra tenant** as the account that bought the subscription. The connection
  always uses the tenant you sign in with, and only when that tenant owns the subscription.
- The resource is an Azure AI Foundry, Azure AI Services or Azure OpenAI resource. Its endpoint looks like
  `https://<name>.services.ai.azure.com`, `https://<name>.openai.azure.com` or `https://<name>.cognitiveservices.azure.com`.
- The resource accepts **public network traffic**. The gateway connects over the internet with TLS; resources reachable only
  through private endpoints are not supported.

## Step 1: add the connector to your tenant

This needs an administrator who may add enterprise applications: Global Administrator, Application Administrator or Cloud
Application Administrator. Use either option.

- **Admin consent link.** On the **Connect your Foundry** page, select **Grant admin consent**. Microsoft shows the connector's
  name and its one permission; accept for your organization. You come back to the page with a confirmation.
- **Azure CLI** (for example in Azure Cloud Shell):

  ```bash
  az ad sp create --id 7154fd27-4506-4cd5-8e3a-b2e5208d0846
  ```

## Step 2: give the connector a role on your resource

The connector needs permission to call deployments on your resource, and nothing more. Two options:

| Role | What it allows | |
|---|---|---|
| **DCA Model Gateway Inference** (custom) | Calls to your deployments only. It cannot list keys, read connection secrets, or read or change the resource's settings. | Recommended |
| **Cognitive Services User** (built-in) | The same calls, **plus** listing the resource's keys and reading its settings | Quicker to assign; broader than needed |

**Recommended: the custom role.** Create it once per Azure subscription, then assign it. Creating a role needs Owner or
User Access Administrator on the subscription.

```bash
SUB=$(az account show --query id -o tsv)
az role definition create --role-definition '{
  "Name": "DCA Model Gateway Inference",
  "Description": "Lets DCA Model Gateway call model deployments. Data plane only: no keys, no secrets, no settings.",
  "Actions": [],
  "DataActions": ["Microsoft.CognitiveServices/*"],
  "AssignableScopes": ["/subscriptions/'"$SUB"'"]
}'
az role assignment create --assignee 7154fd27-4506-4cd5-8e3a-b2e5208d0846 \
  --role "DCA Model Gateway Inference" \
  --scope $(az resource show -g <resource-group> -n <resource-name> \
            --resource-type Microsoft.CognitiveServices/accounts --query id -o tsv)
```

The same definition is in [`samples/connect/dca-model-gateway-inference-role.json`](../samples/connect/dca-model-gateway-inference-role.json).

**Alternative: the built-in role.** In the Azure portal open the resource, then **Access control (IAM)**, **Add role
assignment**, **Cognitive Services User**, and select **DCA Model Gateway Connector** as the member. Or:

```bash
az role assignment create --assignee 7154fd27-4506-4cd5-8e3a-b2e5208d0846 --role "Cognitive Services User" \
  --scope <resource ID of your Foundry resource>
```

**Script:** [`samples/connect/connect-foundry.sh`](../samples/connect/connect-foundry.sh) does steps 1 and 2 with the custom
role (add `--builtin-role` for the built-in one) and prints your endpoint.

A new role assignment can take up to 10 minutes to apply.

## Step 3: enter your endpoint and deployments

On [saas.dcassociatesgroup.com](https://saas.dcassociatesgroup.com), open **Subscriptions**, open the subscription's menu and
choose **Connect your Foundry**.

1. **Foundry endpoint**: the endpoint of the resource from step 2. Any of the three forms above works; paths are ignored.
2. **Deployment names**: map at least **Default**. Each row is a route:

   | Route | Used for | When left empty |
   |---|---|---|
   | Default | Requests that name no model and no route | Required |
   | cheap | `x-dca-route: cheap` | Default deployment |
   | oss-only | `x-dca-route: oss-only`, open-weight models only | **Refused (422)**, never sent to the default |
   | auto | `x-dca-route: auto`, for example your model-router deployment | Default deployment |
   | reasoning | `x-dca-route: reasoning` | Default deployment |
   | code | `x-dca-route: code` | Default deployment |
   | frontier | `x-dca-route: frontier` | Default deployment |
   | embeddings | `/openai/v1/embeddings` | The deployment named in the request |
   | Claude (Anthropic API) | `/anthropic/v1/messages` | The deployment named in the request |

3. **United States data boundary** (optional third column): list only deployments of the *Data Zone Standard (US)* or
   regional US type. Requests with `x-dca-data-boundary: us` use only this column; a route without a US deployment is
   refused with `422 no_eligible_provider`. The gateway relies on your declaration, so declare only deployments that really
   process in the United States.
4. Select **Save and test**. The gateway calls every mapped route once with your key and shows a table: status, the model
   your deployment reported, and the billing tier it was classified as. Fix any row that is not ✅ and select **Test again**.

The page validates what you type. It accepts only the three Azure AI host forms, and deployment names of letters, digits,
`.`, `_` and `-`.

## Change, disconnect, revoke

- **Change the mapping**: edit the page and select **Save and test**. It takes effect at once.
- **Disconnect**: select **Disconnect**. Requests with your key are refused with `409 foundry_not_connected` from then on.
- **Revoke access in Azure**: remove the connector's role assignment, or delete the *DCA Model Gateway Connector* enterprise
  application from your tenant. The gateway then receives `401` from your resource, or cannot sign in at all. Either way
  nothing reaches your deployments.

## More than one resource

The page connects one resource per subscription. To route to deployments in several resources, contact support.
