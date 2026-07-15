# Ollama Setup Guide

This LinkedIn AI agent can run **completely free** using Ollama, a local AI model runner.

## What is Ollama?

Ollama lets you run open-source LLMs (like Mistral, Llama 2) locally on your Mac/Linux/Windows machine. No API costs, no cloud dependencies.

## Installation

### macOS / Linux

1. **Download Ollama**
   ```bash
   # macOS
   brew install ollama
   
   # Or visit: https://ollama.ai/download
   ```

2. **Pull the Mistral model** (7B, ~4GB)
   ```bash
   ollama pull mistral
   ```

3. **Start the Ollama server**
   ```bash
   ollama serve
   ```
   
   You should see: `Listening on 127.0.0.1:11434`

### Windows

1. Download from https://ollama.ai/download
2. Install and run
3. Pull Mistral: `ollama pull mistral`
4. Server starts automatically on `http://localhost:11434`

## Configuration

The LinkedIn agent auto-detects Ollama. Just make sure:

1. **Environment variable** (optional, defaults to true)
   ```bash
   export USE_OLLAMA=true
   ```

2. **Ollama server is running** in another terminal
   ```bash
   ollama serve
   ```

3. **Run the agent**
   ```bash
   cd /Users/toto/Claude\ TubeonAI
   python run_agent.py
   ```

## Model Options

Mistral is the default. You can also use:

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| **mistral** | 7B | Fast | 85% of Claude Haiku |
| llama2 | 7B | Fast | 80% of Claude Haiku |
| neural-chat | 7B | Fast | 75% of Claude Haiku |
| mixtral | 46B | Slower | 90% of Claude Haiku (requires 32GB RAM) |

To switch models, update `OLLAMA_MODEL` in `config.py`:

```python
OLLAMA_MODEL = "llama2"  # Change this
```

Then pull the model:
```bash
ollama pull llama2
```

## Performance Notes

- **First run**: ~30-60 seconds (model loads into memory)
- **Subsequent runs**: ~10-20 seconds per API call (very fast)
- **GPU**: If your Mac/Linux has GPU, Ollama will use it automatically (much faster)
- **Memory**: Mistral needs ~4GB RAM. If you have <8GB total, expect slower performance

## Switching Back to Claude (Paid)

If you want to switch back to Claude Haiku for better quality:

```bash
export USE_OLLAMA=false
python run_agent.py
```

## Troubleshooting

**"Cannot connect to Ollama at http://localhost:11434"**
- Make sure Ollama server is running: `ollama serve`
- Check port 11434 is not blocked

**Slow responses**
- Mistral is slower on CPU-only machines (~20-40 seconds per response)
- Try GPU-enabled setup or use a smaller model

**Out of memory**
- Reduce `max_tokens` in `config.py`
- Or use a smaller model (llama2 vs mistral)

**Quality issues**
- Ollama models are ~15-20% lower quality than Claude
- Some posts may need manual editing
- Switch to Claude for critical content

## Cost Comparison

| Model | Setup | Monthly Cost |
|-------|-------|--------------|
| **Ollama (free)** | Install once | $0 |
| Claude Haiku | API key | $15-30 |
| Claude Sonnet | API key | $150-300 |

**Your choice:** Quality (Claude) vs Cost (Ollama). With Ollama, you're trading ~10% quality for 100% cost savings.
