import type { VercelRequest, VercelResponse } from "@vercel/node";
import { z } from "zod";

const ENCHARGE_API_KEY = process.env.ENCHARGE_API_KEY;
const ENCHARGE_BASE = "https://api.encharge.io/v1";
const LEAD_SOURCE = "img-pivot-protocol";
const OPT_IN_TAG = "img-pivot-protocol-optin";

const leadSchema = z.object({
  firstName: z.string().trim().min(1, "First name is required."),
  email: z.string().trim().email("Please enter a valid email address."),
});

async function enchargeRequest(
  path: string,
  body: Record<string, unknown>,
  apiKey: string
): Promise<Response> {
  return fetch(`${ENCHARGE_BASE}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Encharge-Token": apiKey,
    },
    body: JSON.stringify(body),
  });
}

export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  if (!ENCHARGE_API_KEY) {
    console.error("ENCHARGE_API_KEY is not configured.");
    return res
      .status(500)
      .json({ error: "Server is not configured. Please try again later." });
  }

  const parsed = leadSchema.safeParse(req.body);
  if (!parsed.success) {
    return res
      .status(400)
      .json({ error: parsed.error.issues[0]?.message ?? "Invalid input." });
  }
  const { firstName, email } = parsed.data;

  try {
    await enchargeRequest(
      "/people",
      { email, firstName, leadSource: LEAD_SOURCE },
      ENCHARGE_API_KEY
    );
    await enchargeRequest(
      "/tags",
      { tag: OPT_IN_TAG, users: [{ email }] },
      ENCHARGE_API_KEY
    );
    return res.status(200).json({ ok: true });
  } catch (err: unknown) {
    console.error("Encharge API error:", err);
    return res
      .status(500)
      .json({ error: "Something went wrong. Please try again." });
  }
}
