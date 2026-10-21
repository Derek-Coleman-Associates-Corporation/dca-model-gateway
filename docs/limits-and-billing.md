# Limits and billing

## Per-key limits

Each gateway key has two limits. They protect your Foundry and your bill from runaway clients. Every key of a subscription
has its own counters, so one busy tenant cannot use up another tenant's allowance.

| Plan | Tokens per minute | Tokens per calendar month |
|---|---|---|
| Team | 60,000 | 500,000,000 |
| Partner Edition | 120,000 | 2,500,000,000 |

- Over the per-minute allowance, the gateway answers `429` with `retry-after`. Prompt tokens are estimated before the
  request is forwarded, so an oversized prompt is refused without reaching your deployment.
- Over the monthly cap, the gateway answers `403` until the next calendar month (UTC).
- Every response reports what is left: `x-dca-remaining-tokens` for this minute and `x-dca-remaining-quota-tokens` for this month.

**Your own monthly budget per key.** On the [Tenant keys](tenant-keys.md) page you can give any key a lower monthly budget
(at least 1,000 tokens), for example the amount a customer pays you for. Over its budget the key is refused with `403` until
the next calendar month (UTC), while your other keys keep working. Responses on a key with a budget also carry
`x-dca-budget-remaining-tokens`. The plan's monthly cap above still applies.

Your deployments keep their own quotas in Azure as well. Whichever limit is lower applies first.

## Keys per subscription

| Plan | Keys (the Default key included) | Active tenants included each month |
|---|---|---|
| Team | 25 | 5 |
| Partner Edition | 100 | 25 |

Revoked keys do not count towards the number of keys.

## What you pay

You receive two separate charges:

1. **Model usage** is billed by Microsoft on your own Azure subscription, as with any direct call to your Foundry deployments.
   DCA Model Gateway does not resell or mark up model access.
2. **DCA Model Gateway** is billed through Microsoft Marketplace on the same Azure invoice: a monthly plan fee, with routed
   tokens beyond the included amount metered per million.

| Plan | Monthly fee | Included each month | Beyond the included amount |
|---|---|---|---|
| Team | US$199 | 200M open-weight and 25M frontier routed tokens; 5 active tenants | US$0.25 per 1M open-weight, US$0.60 per 1M frontier; US$15 per additional active tenant |
| Partner Edition | US$499 | 1,000M open-weight and 100M frontier routed tokens; 25 active tenants | Same rates |

Prices as listed on 2026-10-15. The [Marketplace listing](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/dcassociatesgroupinc.dca-model-gateway?tab=Overview)
is authoritative. Taxes and currency follow your Azure billing account.

**Routed tokens** are the prompt and completion tokens of every request that reached your deployment. Refused requests
(4xx and 5xx from the gateway) are not counted.

**Tier.** A request counts as *open-weight* when its deployment serves an open-weight model family (for example Llama,
DeepSeek, gpt-oss, Mistral, Phi, Qwen, Gemma); everything else, including GPT and Claude models, counts as *frontier*. The
gateway takes the model name each deployment reported in your last connection test, shown in the **Billing tier** column. A
deployment the test has not called counts as *frontier*, so map and test every deployment you use (**Save and test** on the
Connect page). For Google Vertex AI the model id itself decides: Gemini and Claude are frontier; open-weight models such as
gpt-oss, DeepSeek, Qwen, GLM, Llama or Gemma are open-weight. Only a valid answer in the connection test sets a tier: a
throttled (429) or malformed answer leaves it unconfirmed (frontier) until a later test succeeds, and a tier never carries
over when a deployment name is pointed at another endpoint or project. The `oss-only` route is enforced against this tier:
it is refused (`422 not_open_weight`) unless the mapped deployment bills as open-weight.

**Active tenants.** An active tenant is a key, the Default key included, that routed at least one token in the
subscription's monthly billing period. Keys that are never used are free. Beyond the plan's included number, each
additional active tenant is charged once for that billing period, however much it routes. The Tenant keys page shows how
many keys are active in the current period.

## Where to see usage

- Per request: the `x-dca-tokens-consumed` response header.
- Per key: the [Tenant keys](tenant-keys.md) page shows each key's tokens for the month you choose, and **Download usage
  (CSV)** gives tokens per day, key, deployment, billing tier, route and data boundary, for rebilling your own customers.
- Per month: the Marketplace charges for DCA Model Gateway in Azure Cost Management and on your invoice, and your
  deployments' own metrics in Azure Monitor.
