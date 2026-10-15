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

## 422 `route_not_configured` or `no_eligible_provider`

- `route_not_configured`: the route you sent has no deployment and no fallback. `oss-only` never falls back to the default
  deployment.
- `no_eligible_provider`: you sent `x-dca-data-boundary: us`, and no deployment is declared for the United States boundary
  for that request.

Map the route, or the US column, on the Connect your Foundry page.

## 429 or 403 without an `error.code`

You reached this key's per-minute (429) or monthly (403) token limit. Wait `retry-after` seconds, or see
[Limits and billing](limits-and-billing.md). A 429 *with* your deployment's own error body comes from your deployment's
quota in Azure.

## 401 `Access denied due to invalid subscription key`

The key is wrong, was regenerated, or the subscription is cancelled. Copy the current key, or choose **Regenerate gateway key**.

## My subscription shows Pending activation

Our team confirms new subscriptions before billing starts. You can connect your Foundry in the meantime. The key works as
soon as the status is **Subscribed**.

## The OpenAI SDK returns 401 although the key is right

The OpenAI SDKs send the key as `Authorization: Bearer`. Add the `api-key` header:
`default_headers={"api-key": key}` in Python, `defaultHeaders: { "api-key": key }` in Node.js.

## Still stuck?

Email support@dcassociatesgroup.com with your Marketplace subscription ID, the time of a failing request (UTC), and the full
error body. Never send your gateway key.
