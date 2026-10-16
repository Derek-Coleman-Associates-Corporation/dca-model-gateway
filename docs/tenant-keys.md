# Tenant keys

Give each of your customers or applications its own gateway key. Every key of a subscription reaches the same connected
Foundry, but each one has its own limits, its own optional monthly budget and its own usage. You can bill your customers
for what they used, and cut one off without touching the others.

## Open the page

1. Open [saas.dcassociatesgroup.com](https://saas.dcassociatesgroup.com) and select **Subscriptions**.
2. Open the subscription's menu and choose **Tenant keys**.

The page shows how many keys are in use out of the plan's allowance, how many keys were active in the current billing
period, and a table of every key: name, key ID, state, tokens in the chosen month and monthly budget.

The first key, issued when the subscription is activated, is called **Default**. Keys can be added and changed once the
subscription shows **Subscribed**.

| Plan | Keys (Default included) | Active tenants included each month |
|---|---|---|
| Team | 25 | 5 |
| Partner Edition | 100 | 25 |

## Add a key

1. Under **Add a key**, enter a name: the customer or application the key is for. Use letters, digits, spaces, `.`, `_` and
   `-`, up to 40 characters.
2. Optionally enter a **monthly budget** in tokens (see below).
3. Select **Add key**. The new key is shown **once**. Copy it into your secret manager, or hand it to your customer over a
   secure channel.

New keys can take up to a minute to be accepted everywhere. A `401` in the first seconds is normal; retry.

Use a new key exactly like the Default key: send it in the `api-key` header (OpenAI APIs) or `x-api-key` (Anthropic API). See
the [API reference](api-reference.md).

## Monthly budgets

A budget caps one key's tokens per calendar month (UTC), below the plan's own per-key cap. Use it to match what each of your
customers pays you.

- Enter the number of tokens next to the key and select **Set**. To remove the budget, leave the field empty and select
  **Set**.
- A budget must be at least 1,000 tokens.
- When a key reaches its budget, its requests are refused with `403` until the next month. Your other keys keep working.
- Responses on a key with a budget carry `x-dca-budget-remaining-tokens`.

## Regenerate or revoke

- **Regenerate** issues a new secret for that key. The previous secret stops working immediately. The key keeps its ID,
  name, budget and usage.
- **Revoke** ends an additional key for good: requests with it are refused from then on, and it no longer counts towards the
  plan's number of keys. The Default key cannot be revoked; it follows the subscription.

If the subscription is suspended, every key is suspended with it and resumes when it is reinstated. A cancelled
subscription cancels all of its keys.

## Usage and export

- Choose a month under **Usage for** and select **Show** to see each key's tokens in that month (the last six months are
  available).
- **Download usage (CSV)** exports the chosen month with one row per day, key, deployment, route and data boundary:

  | Column | Meaning |
  |---|---|
  | `date_utc` | Day (UTC) |
  | `key_id` | The key's ID, as shown in the table |
  | `key_name` | The name you gave the key |
  | `deployment` | The deployment that served the requests |
  | `tier` | `openweight` or `frontier`, the billing tier |
  | `route` | The route the requests used |
  | `data_boundary` | `any` or `us` |
  | `tokens` | Prompt and completion tokens |

## Billing

Keys themselves cost nothing. A key counts as an **active tenant** in a billing period once it routes at least one token.
The plan includes a number of active tenants each month; each additional active tenant is charged once for that billing
period through Microsoft Marketplace. Routed tokens are billed the same way whichever key sent them. See
[Limits and billing](limits-and-billing.md).
