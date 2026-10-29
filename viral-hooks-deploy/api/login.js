import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { accessCode } = req.body;
  if (!accessCode) {
    return res.status(400).json({ ok: false, error: 'Access code is required' });
  }

  const code = accessCode.trim().toLowerCase();
  const subscriberId = await kv.get(`code:${code}`);
  if (!subscriberId) {
    return res.status(401).json({ ok: false, error: 'Invalid or inactive access code' });
  }

  res.setHeader('Set-Cookie', `access=${encodeURIComponent(code)}; HttpOnly; Path=/; Max-Age=2592000; SameSite=Lax; Secure`);
  res.json({ ok: true });
}
