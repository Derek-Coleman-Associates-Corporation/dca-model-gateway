# Getting started

## What you need

- An Azure subscription that can buy Microsoft Marketplace SaaS offers (pay-as-you-go, Enterprise Agreement or Microsoft
  Customer Agreement; sponsored and free-credit subscriptions cannot buy).
- A **work or school account** (Microsoft Entra ID) in the organization that buys. Personal Microsoft accounts can buy, but
  they cannot connect a Foundry, because the connection is made in your organization's Entra tenant.
- An Azure AI Foundry, Azure AI Services or Azure OpenAI resource in that tenant, with at least one deployment.

## 1. Subscribe and activate

1. Open [DCA Model Gateway on Microsoft Marketplace](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/dcassociatesgroupinc.dca-model-gateway?tab=Overview)
   and choose a plan. *Team* is listed publicly; *Partner Edition* is offered privately, so contact us for it.
2. After the purchase, select **Configure account now** in the Azure portal. It opens the activation page at
   `https://saas.dcassociatesgroup.com`.
3. Sign in with your work account. The page shows the subscription, offer, plan and your tenant.
4. Accept the privacy notice, optionally tell us your organization's country, and select **Subscribe**.

If the subscription then shows **Pending activation**, our team confirms new subscriptions before billing starts. You are not
billed until it is activated. Connect your Foundry meanwhile (step 2); your key works as soon as the status is **Subscribed**.

## 2. Connect your Foundry

Follow [Connect your Foundry](connect-your-foundry.md). In short: add the *DCA Model Gateway Connector* to your tenant, give it
the **Cognitive Services User** role on your Foundry resource, then enter your endpoint and deployments on the
**Connect your Foundry** page and select **Save and test**.

Until a Foundry is connected, every request with your key is refused with `409 foundry_not_connected` and nothing is
forwarded anywhere.

## 3. Get your gateway key

1. Open [saas.dcassociatesgroup.com](https://saas.dcassociatesgroup.com) and select **Subscriptions**.
2. Open the subscription's menu and choose **Regenerate gateway key**.
3. Copy the key from the banner. It is shown **once**; store it in your secret manager.

Your endpoint is `https://ai-gateway-east-us1.azure-api.net/gateway`. Each subscription has one gateway key.

**Rotating the key.** Choose **Regenerate gateway key** again. The new key works immediately and the previous key stops
working at the same moment, so update your applications first if you need a seamless switch.

## 4. Send your first request

```bash
export DCA_GATEWAY_KEY="<your gateway key>"
curl https://ai-gateway-east-us1.azure-api.net/gateway/openai/v1/chat/completions \
  -H "api-key: $DCA_GATEWAY_KEY" -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

The response headers tell you what happened:

| Header | Example | Meaning |
|---|---|---|
| `x-dca-backend` | `customer-foundry` | Your own Foundry served the request |
| `x-dca-model` | `gpt-4.1-mini` | The deployment that served it |
| `x-dca-remaining-quota-tokens` | `499999824` | Tokens left this month on this key |

Next: [API reference](api-reference.md) for routes, the data boundary and every header.

## Changing plan or cancelling

- **Change plan**: on [saas.dcassociatesgroup.com](https://saas.dcassociatesgroup.com) open the subscription's menu, or use the
  SaaS resource in the Azure portal. Your key and your Foundry connection stay the same; the new plan's limits apply at once.
- **Cancel**: in the Azure portal, open the SaaS resource and cancel the subscription. The key stops working, and the
  Foundry connection is deleted within an hour. Remove the connector's role assignment in your Azure subscription as well if
  you no longer need it.
