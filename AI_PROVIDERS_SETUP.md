# AI Providers Setup Guide

Your LinkedIn AI agent now supports **3 AI providers** with intelligent fallback:

1. **Groq API** (free, fastest) ⚡
2. **Ollama** (free, local) 📍
3. **Claude Haiku** (paid, best quality) 🧠

## Quick Start (Recommended: Groq)

### Step 1: Sign Up for Groq (2 minutes)
```bash
# Visit https://console.groq.com
# Sign up with email or GitHub
# Copy your API key
```

### Step 2: Set Environment Variable
```bash
export GROQ_API_KEY="your_key_here"
```

### Step 3: Run Agent
```bash
cd /Users/toto/Claude\ TubeonAI
python run_agent.py
```

Done! Agent auto-detects Groq and uses it.

---

## Configuration

### AUTO MODE (Recommended)
```bash
# No setup needed - tries in order: Groq → Ollama → Claude
export AI_PROVIDER=auto
python run_agent.py
```

### Force Groq
```bash
export AI_PROVIDER=groq
export GROQ_API_KEY="your_key"
python run_agent.py
```

### Force Ollama
```bash
export AI_PROVIDER=ollama
# Make sure Ollama server is running: ollama serve
python run_agent.py
```

### Force Claude
```bash
export AI_PROVIDER=claude
# Uses ANTHROPIC_API_KEY from .env
python run_agent.py
```

---

## Provider Comparison

| Feature | Groq | Ollama | Claude |
|---------|------|--------|--------|
| **Cost** | FREE (tier) | FREE | Paid (~$20/mo) |
| **Setup** | 2 min | 5 min | 0 min |
| **Speed** | ⚡ Ultra fast (3-5s) | 🐢 Slow (15-30s) | 🚀 Fast (5-10s) |
| **Quality** | 85% | 85% | 100% |
| **Internet** | Required | Optional | Required |
| **Local?** | No | Yes | No |
| **Rate limit** | 30 req/min | Unlimited | Unlimited |

---

## Installation

### Groq (Recommended)
```bash
# Just sign up at https://console.groq.com and get API key
# No installation needed - uses cloud API
export GROQ_API_KEY="your_key"
```

### Ollama
```bash
# macOS
brew install ollama

# Pull model
ollama pull mistral

# Start server in separate terminal
ollama serve
```

### Claude (Existing)
```bash
# Already set in .env file
export ANTHROPIC_API_KEY="your_key"
```

---

## Fallback Behavior

With `AI_PROVIDER=auto`:

```
1. Try Groq API
   ✓ Success → Use Groq
   ✗ Fail → Try Ollama

2. Try Ollama (local)
   ✓ Success → Use Ollama
   ✗ Fail → Fall back to Claude

3. Use Claude
   ✓ Success → Use Claude
   ✗ Fail → Exit with error
```

---

## Real-World Scenarios

### Scenario A: Best Free Option
```bash
export GROQ_API_KEY="your_key"
python run_agent.py
# → Uses Groq (fast, free, cloud)
```

### Scenario B: Complete Offline
```bash
export AI_PROVIDER=ollama
ollama serve  # in another terminal
python run_agent.py
# → Uses Ollama (local, no internet needed)
```

### Scenario C: Best Quality
```bash
export AI_PROVIDER=claude
python run_agent.py
# → Uses Claude Haiku (paid, best posts)
```

### Scenario D: Smart Fallback
```bash
# No export needed, uses auto mode
export GROQ_API_KEY="your_key"
# If Groq fails, automatically falls back to local Ollama
# If Ollama fails, falls back to Claude
python run_agent.py
```

---

## Troubleshooting

### "Cannot connect to Groq API"
- Check internet connection
- Verify `GROQ_API_KEY` is set: `echo $GROQ_API_KEY`
- Visit https://console.groq.com to confirm key is valid

### "Cannot connect to Ollama"
- Make sure Ollama server is running: `ollama serve`
- Check Ollama is listening on `localhost:11434`
- `curl http://localhost:11434/api/tags` should work

### "Claude API key not found"
- Check `.env` file has `ANTHROPIC_API_KEY`
- Run: `source .env && echo $ANTHROPIC_API_KEY`

---

## Cost Analysis (30 posts/day × 30 days = 900 posts/month)

| Provider | Cost | Posts/month | Cost/post |
|----------|------|-------------|-----------|
| **Groq (free)** | $0 | 900+ | $0.00 |
| **Ollama** | $0 | 900+ | $0.00 |
| **Claude Haiku** | ~$20 | 900 | $0.02 |

---

## Recommendation

**Start with Groq.** It's:
- ✅ Free (forever)
- ✅ Fast (3-5s per post)
- ✅ Zero setup (cloud API)
- ✅ Auto-fallback if it goes down

If you want complete offline capability, keep Ollama running as backup.

If you want best quality, switch to Claude anytime: `export AI_PROVIDER=claude`
