"""Let the gateway pick the deployment: send x-dca-route and the gateway uses the deployment you mapped to that route
on the Connect your Foundry page (the `model` value is then ignored). Routes you left empty use your default deployment,
except oss-only, which is refused (422) rather than sent to a non-open-weight model."""
from openai import OpenAI, APIStatusError

from _gateway import GATEWAY_URL, KEY

client = OpenAI(base_url=f"{GATEWAY_URL}/openai/v1", api_key=KEY, default_headers={"api-key": KEY})

for route in ("cheap", "reasoning", "frontier", "oss-only"):
    try:
        r = client.chat.completions.with_raw_response.create(
            model="route-decides",
            messages=[{"role": "user", "content": "Reply with the single word OK"}],
            max_completion_tokens=8,
            extra_headers={"x-dca-route": route},
        )
        print(f"{route:<10} -> {r.status_code} deployment={r.headers.get('x-dca-model')} model={r.parse().model}")
    except APIStatusError as e:
        error = (e.body or {}).get("code") if isinstance(e.body, dict) else None
        print(f"{route:<10} -> {e.status_code} {error or ''}: {str(e.message)[:110]}")
