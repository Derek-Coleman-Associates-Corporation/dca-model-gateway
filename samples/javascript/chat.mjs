// Chat completion through DCA Model Gateway with the official OpenAI Node.js SDK.
// DCA_GATEWAY_KEY = your gateway key; DCA_DEPLOYMENT = a deployment in your own Azure AI Foundry.
import OpenAI from "openai";

const gatewayUrl = (process.env.DCA_GATEWAY_URL ?? "https://ai-gateway-east-us1.azure-api.net/gateway").replace(/\/$/, "");
const key = process.env.DCA_GATEWAY_KEY;
if (!key) throw new Error("Set DCA_GATEWAY_KEY to your gateway key.");

const client = new OpenAI({
  baseURL: `${gatewayUrl}/openai/v1`,
  apiKey: key,
  defaultHeaders: { "api-key": key }, // the gateway reads the key from the api-key header
});

const { data, response } = await client.chat.completions
  .create({
    model: process.env.DCA_DEPLOYMENT ?? "gpt-4.1-mini",
    messages: [{ role: "user", content: "In one sentence, what is an API gateway?" }],
    max_completion_tokens: 60,
  })
  .withResponse();

console.log(data.choices[0].message.content);
console.log("served by:", response.headers.get("x-dca-backend"), "| deployment:", response.headers.get("x-dca-model"), "| model:", data.model);
