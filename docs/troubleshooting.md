# Troubleshooting

Start with the connection checker. It sends one small request and explains the result:

```bash
export DCA_GATEWAY_KEY="<your gateway key>"
python3 samples/python/check_connection.py
```

## Every request returns 409 `foundry_not_connected`

No Foundry is connected to this subscription, or it was disconnected. Open **Connect your Foundry** from the subscription's
menu on [saas.dcassociatesgroup.com](https://saas.dcassociatesgroup.com) and save a connection.

## 502 `foundry_auth_failed` with `AADSTS700016`

The DCA Model Gateway Connector is not in your Microsoft Entra tenant yet. An administrator does step 1 of
[Connect your Foundry](connect-your-foundry.md). For other `AADSTS` codes see [Errors](errors.md#foundry_auth_failed-the-aadsts-code).

## 401 `PermissionDenied` from your Foundry

The connector reached your resource but has no role there. Assign the role (step 2), wait up to 10 minutes, then select
**Test again** on the Connect your Foundry page.

## 403 from your Foundry

Your resource refuses public network traffic. In the Azure portal, open the resource's **Networking** settings and allow
access from all networks, or from selected networks that include the internet route the gateway uses. Resources reachable
only through private endpoints are not supported.

## 404 `DeploymentNotFound`

The deployment name in `model`, or in your mapping, does not exist on the connected resource. Names are case-sensitive and
are the *deployment* names, not the model names.

## 422 `route_not_configured`, `not_open_weight` or `no_eligible_provider`

- `route_not_configured`: the route you sent has no deployment and no fallback. `oss-only` never falls back to the default
  deployment.
- `not_open_weight`: you sent `x-dca-route: oss-only`, and the deployment mapped to it is billed as frontier, or its tier is
  not confirmed yet. Map an open-weight deployment, or run **Save and test** so the deployment's model is recorded.
- `no_eligible_provider`: you sent `x-dca-data-boundary: us`, and no deployment is declared for the United States boundary
  for that request.

Map the route, or the US column, on the Connect your Foundry page.

## 400 `Tenant provided in token does not match resource token`

The endpoint you connected belongs to a resource in a different Microsoft Entra tenant from the one that owns your
subscription, for example a subsidiary's or a partner's tenant. The gateway always signs in to the tenant that bought the
subscription, and Azure refuses a token from any other tenant. Connect a resource in your own tenant.

## 429 or 403 without an `error.code`

You reached this key's per-minute (429) or monthly (403) token limit, or the monthly budget you set for the key. Wait
`retry-after` seconds, check the key's budget on [Tenant keys](tenant-keys.md), or see [Limits and billing](limits-and-billing.md). A 429 *with* your deployment's own error body comes from your deployment's
quota in Azure.

## 401 `Access denied due to invalid subscription key`

The key is wrong, was regenerated or revoked, or the subscription is cancelled. Copy the current key, or regenerate it on the
Subscriptions or Tenant keys page.

## My subscription shows Pending activation

Activation did not finish. In the Azure portal, open the SaaS resource, select **Configure account now** and then
**Activate**. If it still shows Pending activation, contact support with your Marketplace subscription ID.

## I cannot add a key

Keys can be added once the subscription shows **Subscribed**, up to the plan's number of keys (revoked keys do not count).
See [Limits and billing](limits-and-billing.md#keys-per-subscription).

## The OpenAI SDK returns 401 although the key is right

The OpenAI SDKs send the key as `Authorization: Bearer`. Add the `api-key` header:
`default_headers={"api-key": key}` in Python, `defaultHeaders: { "api-key": key }` in Node.js.

## Still stuck?

Email support@dcassociatesgroup.com with your Marketplace subscription ID, the time of a failing request (UTC), and the full
error body. Never send your gateway key.
