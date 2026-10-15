# Limits and billing

## Per-key limits

Each gateway key has two limits. They protect your Foundry and your bill from runaway clients.

| Plan | Tokens per minute | Tokens per calendar month |
|---|---|---|
| Team | 60,000 | 500,000,000 |
| Partner Edition | 120,000 | 2,500,000,000 |

- Over the per-minute allowance, the gateway answers `429` with `retry-after`. Prompt tokens are estimated before the
  request is forwarded, so an oversized prompt is refused without reaching your deployment.
- Over the monthly cap, the gateway answers `403` until the next calendar month (UTC).
- Every response reports what is left: `x-dca-remaining-tokens` for this minute and `x-dca-remaining-quota-tokens` for this month.

Your deployments keep their own quotas in Azure as well. Whichever limit is lower applies first.

## What you pay

You receive two separate charges:

1. **Model usage** is billed by Microsoft on your own Azure subscription, as with any direct call to your Foundry deployments.
   DCA Model Gateway does not resell or mark up model access.
2. **DCA Model Gateway** is billed through Microsoft Marketplace on the same Azure invoice: a monthly plan fee, with routed
   tokens beyond the included amount metered per million.

| Plan | Monthly fee | Included each month | Beyond the included amount |
|---|---|---|---|
| Team | US$199 | 200M open-weight and 25M frontier routed tokens | US$0.25 per 1M open-weight, US$0.60 per 1M frontier |
| Partner Edition | US$499 | 1,000M open-weight and 100M frontier routed tokens | Same rates |

Prices as listed on 2026-10-15. The [Marketplace listing](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/dcassociatesgroupinc.dca-model-gateway?tab=Overview)
is authoritative. Taxes and currency follow your Azure billing account.

**Routed tokens** are the prompt and completion tokens of every request that reached your deployment. Refused requests
(4xx and 5xx from the gateway) are not counted.

**Tier.** A request counts as *open-weight* when its deployment serves an open-weight model family (for example Llama,
DeepSeek, gpt-oss, Mistral, Phi, Qwen, Gemma); everything else, including GPT and Claude models, counts as *frontier*. The
gateway takes the model name each deployment reported in your last connection test, shown in the **Billing tier** column. For
a deployment the test has not called, it uses the deployment's name.

**Active tenants.** The plan lists an *active tenants* meter. Each subscription has one gateway key, and this meter is not
charged.

## Where to see usage

- Per request: the `x-dca-tokens-consumed` response header.
- Per month: the Marketplace charges for DCA Model Gateway in Azure Cost Management and on your invoice, and your
  deployments' own metrics in Azure Monitor.
