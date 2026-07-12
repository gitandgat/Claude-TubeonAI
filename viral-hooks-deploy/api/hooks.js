import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const cookies = parseCookies(req.headers.cookie || '');
  const code = cookies.access ? decodeURIComponent(cookies.access) : null;

  const subscriberId = code ? await kv.get(`code:${code}`) : null;
  if (!subscriberId) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  const { prompt, maxTokens = 1000, system } = req.body;

  if (!prompt) {
    return res.status(400).json({ error: 'prompt is required' });
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    return res.status(500).json({ error: 'ANTHROPIC_API_KEY not configured on server' });
  }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: maxTokens,
        system: system || 'You are a helpful assistant.',
        messages: [{ role: 'user', content: prompt }]
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      return res.status(response.status).json({
        error: errorData.error?.message || 'Anthropic API error'
      });
    }

    const data = await response.json();
    const text = data.content?.[0]?.text || '';
    res.json({ text });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

function parseCookies(header) {
  return Object.fromEntries(
    header.split(';').map(c => c.trim().split('=')).filter(p => p.length === 2)
  );
}
