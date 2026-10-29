import express from 'express';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 3001;
const ACCESS_PASSWORD = process.env.FOUNDING_ACCESS_PASSWORD;

app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(cookieParser());

// Health check (no auth required)
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

const requireAccess = (req, res, next) => {
  if (!ACCESS_PASSWORD) {
    return res.status(500).send('FOUNDING_ACCESS_PASSWORD not configured on server');
  }
  if (req.cookies?.access === ACCESS_PASSWORD) {
    return next();
  }
  if (req.path === '/login' || req.path === '/api/login') {
    return next();
  }
  res.redirect('/login');
};

app.use(requireAccess);
app.use(express.static(__dirname));

// Login page
app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'login.html'));
});

app.post('/api/login', (req, res) => {
  const { password } = req.body;
  if (password === ACCESS_PASSWORD) {
    res.cookie('access', ACCESS_PASSWORD, {
      httpOnly: true,
      maxAge: 1000 * 60 * 60 * 24 * 365,
      sameSite: 'lax'
    });
    return res.json({ ok: true });
  }
  res.status(401).json({ ok: false, error: 'Incorrect password' });
});

// Serve the HTML app at root
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'viral-hooks-working.html'));
});

// Proxy API calls to Anthropic
app.post('/api/hooks', async (req, res) => {
  try {
    const { prompt, maxTokens = 1000, system } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'prompt is required' });
    }

    if (!process.env.ANTHROPIC_API_KEY) {
      return res.status(500).json({ error: 'ANTHROPIC_API_KEY not configured on server' });
    }

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
    console.error('Error calling Anthropic API:', error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`🎯 Viral Hooks server running on http://localhost:${PORT}`);
  console.log(`📍 API endpoint: POST http://localhost:${PORT}/api/hooks`);
  console.log(`🏥 Health check: GET http://localhost:${PORT}/health`);
});
