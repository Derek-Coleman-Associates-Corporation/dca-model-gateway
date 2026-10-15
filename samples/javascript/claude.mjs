// Claude through DCA Model Gateway with the official Anthropic TypeScript/JavaScript SDK (key travels in x-api-key).
import Anthropic from "@anthropic-ai/sdk";

const gatewayUrl = (process.env.DCA_GATEWAY_URL ?? "https://ai-gateway-east-us1.azure-api.net/gateway").replace(/\/$/, "");
const key = process.env.DCA_GATEWAY_KEY;
if (!key) throw new Error("Set DCA_GATEWAY_KEY to your gateway key.");

const client = new Anthropic({ baseURL: `${gatewayUrl}/anthropic`, apiKey: key });

const message = await client.messages.create({
  model: process.env.DCA_CLAUDE_DEPLOYMENT ?? "claude-sonnet-4-6",
  max_tokens: 64,
  messages: [{ role: "user", content: "In one sentence, what does a model gateway do?" }],
});
console.log(message.content[0].text, "|", message.model);
