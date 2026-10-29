# Viral Hooks — Secure Backend Setup

A React app with a secure Express backend that keeps your Anthropic API key on the server (never exposed in the browser).

## Files

- **`hooks-server.js`** — Express backend that proxies API calls
- **`viral-hooks-secure.html`** — Frontend (calls the backend, not Anthropic directly)
- **`package.json`** — Dependencies & scripts
- **`.env`** — Your secrets (ANTHROPIC_API_KEY)

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Verify `.env` Has Your API Key
```bash
cat .env | grep ANTHROPIC_API_KEY
```

Should output:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Start the Backend
```bash
npm run hooks-server
```

You should see:
```
🎯 Viral Hooks server running on http://localhost:3001
📍 API endpoint: POST http://localhost:3001/api/hooks
🏥 Health check: GET http://localhost:3001/health
```

### 4. Open the Frontend
```bash
# macOS
open viral-hooks-secure.html

# Or drag into your browser
# http://localhost:3001/viral-hooks-secure.html (optional - if serving)
```

The app will auto-detect the backend and show a green "✓ Connected" status.

## How It Works

```
Frontend (browser)
    ↓ POST /api/hooks (prompt, system, maxTokens)
Backend (Node.js)
    ↓ reads ANTHROPIC_API_KEY from .env
    ↓ calls Anthropic API
    ↓ returns response.text
Frontend (displays results)
```

**Security benefit:** Your API key never leaves the server.

## API Endpoint

### `POST /api/hooks`

**Request:**
```json
{
  "prompt": "Your prompt here",
  "maxTokens": 1000,
  "system": "Your system message (optional)"
}
```

**Response:**
```json
{
  "text": "Claude's response here"
}
```

**Error Response:**
```json
{
  "error": "Error message"
}
```

## Running with Nodemon (Development)

For auto-restart on file changes:
```bash
npm run dev
```

## Deploying to Production

### Option 1: Railway (Recommended)
```bash
# Install Railway CLI
brew install railway

# Login and link
railway login
railway link

# Deploy
railway up
```

Add environment variable in Railway dashboard:
- `ANTHROPIC_API_KEY=sk-ant-...`

### Option 2: Vercel Functions
Create `api/hooks.js`:
```javascript
import dotenv from 'dotenv';
dotenv.config();

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { prompt, maxTokens = 1000, system } = req.body;

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: maxTokens,
        system: system || 'You are a helpful assistant.',
        messages: [{ role: 'user', content: prompt }]
      })
    });

    const data = await response.json();
    res.json({ text: data.content?.[0]?.text || '' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
```

Then update `viral-hooks-secure.html`:
```javascript
const API_BASE = process.env.REACT_APP_API_URL || 
  (window.location.hostname === 'localhost' 
    ? 'http://localhost:3001' 
    : 'https://your-domain.vercel.app/api');
```

### Option 3: Self-Hosted (Docker)
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY hooks-server.js .
EXPOSE 3001
CMD ["node", "hooks-server.js"]
```

```bash
docker build -t viral-hooks .
docker run -p 3001:3001 --env-file .env viral-hooks
```

## Troubleshooting

**"Backend server not running"**
- Make sure you ran `npm run hooks-server`
- Check that it's listening on `http://localhost:3001`

**"ANTHROPIC_API_KEY not configured"**
- Verify your `.env` file has `ANTHROPIC_API_KEY=sk-ant-...`
- Restart the server after changing `.env`

**CORS errors**
- The server has CORS enabled for all origins
- If deploying to a different domain, update `cors()` in `hooks-server.js`

**API Key errors (401)**
- Check that your API key is valid
- Test with: `curl -H "x-api-key: YOUR_KEY" https://api.anthropic.com/v1/models`

## Environment Variables

### Local Development
```env
ANTHROPIC_API_KEY=sk-ant-...
PORT=3001
```

### Production (Railway/Vercel)
Set in platform dashboard:
- `ANTHROPIC_API_KEY` — Your Anthropic API key
- `PORT` — Optional, defaults to 3001

## Development

### Using Nodemon
```bash
npm run dev
# Server restarts on file changes
```

### Testing the API Directly
```bash
curl -X POST http://localhost:3001/api/hooks \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "List 3 viral hook patterns",
    "maxTokens": 500
  }'
```

## Modes

### Topic Mode
Enter a topic → Research 5 viral patterns → Repurpose into Crosswalk Wisdom voice

### Paste Mode
Paste a hook → Analyze → Generate 5 adapted hooks

### Optional: Video Script
Generates 60-second script with time markers from first hook

## Features

- ✅ API key never exposed in browser
- ✅ Secure CORS proxy
- ✅ Copy buttons on all results
- ✅ Platform selector (YouTube/TikTok/Instagram/All)
- ✅ Loading stage feedback
- ✅ Error handling
- ✅ Smooth scroll to results
- ✅ Crosswalk Wisdom brand styling

## Scaling

For high traffic, add caching:

```javascript
import NodeCache from 'node-cache';
const cache = new NodeCache({ stdTTL: 3600 }); // 1 hour

app.post('/api/hooks', async (req, res) => {
  const key = `${req.body.prompt}-${req.body.maxTokens}`;
  const cached = cache.get(key);
  if (cached) return res.json({ text: cached });
  
  // ... call API ...
  cache.set(key, data.text);
  res.json({ text: data.text });
});
```

---

**Questions?** Check CLAUDE.md for project context.
