"""Troubleshooting: one small call, then the gateway's verdict in plain words (status, error code, which backend served it)."""
import json
import urllib.error
import urllib.request

from _gateway import GATEWAY_URL, KEY

req = urllib.request.Request(
    f"{GATEWAY_URL}/openai/v1/chat/completions",
    method="POST",
    data=json.dumps({"messages": [{"role": "user", "content": "Reply with OK"}], "max_completion_tokens": 8}).encode(),
    headers={"api-key": KEY, "Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        status, body, headers = r.status, json.loads(r.read()), r.headers
except urllib.error.HTTPError as e:
    status, headers = e.code, e.headers
    try:
        body = json.loads(e.read())
    except ValueError:
        body = {}

print("HTTP", status)
for h in ("x-dca-backend", "x-dca-model", "x-dca-data-boundary", "x-dca-processing-scope", "x-dca-remaining-quota-tokens"):
    if headers.get(h):
        print(f"  {h}: {headers.get(h)}")
error = body.get("error") if isinstance(body, dict) else None
if isinstance(error, dict):
    print("  error:", error.get("code"), "-", error.get("message"))
    if error.get("aadsts"):
        print("  Microsoft Entra code:", error.get("aadsts"))
elif status == 200:
    print("  OK: your default deployment answered as", body.get("model"))
