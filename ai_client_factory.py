"""
AI Client Factory with intelligent fallback.
Priority: Groq (fast, free) → Ollama (local, free) → Claude (paid, best)
"""

import os
from linkedin_agent.config import AI_PROVIDER, GROQ_API_KEY, GROQ_MODEL, OLLAMA_MODEL, OLLAMA_BASE_URL

def get_ai_client():
    """
    Get AI client with fallback logic.
    Returns: client object with .create() method
    """
    provider = AI_PROVIDER

    # AUTO mode: Ollama (free, local) first, Claude Haiku as fallback.
    # Groq is excluded from auto until its API key is valid — force with
    # AI_PROVIDER=groq to use it.
    if provider == "auto":
        try:
            from ollama_client import OllamaClient
            client = OllamaClient(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
            # Live test: confirms server is up AND the model is pulled
            client.generate("Reply with the single word: ok", max_tokens=5)
            print(f"✓ Using Ollama ({OLLAMA_MODEL} — free, local)")
            return ("ollama", client)
        except Exception as e:
            print(f"⚠ Ollama unavailable: {e}. Falling back to Claude Haiku...")

        from anthropic import Anthropic
        print("✓ Using Claude Haiku (paid fallback)")
        return ("claude", Anthropic())

    # EXPLICIT mode: Use specified provider
    elif provider == "groq":
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set. Sign up free at https://console.groq.com")
        from groq_client import GroqClient
        print("✓ Using Groq API (forced)")
        return ("groq", GroqClient(api_key=GROQ_API_KEY, model=GROQ_MODEL))

    elif provider == "ollama":
        from ollama_client import OllamaClient
        print("✓ Using Ollama (forced)")
        return ("ollama", OllamaClient(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL))

    elif provider == "claude":
        from anthropic import Anthropic
        print("✓ Using Claude Haiku (forced)")
        return ("claude", Anthropic())

    else:
        raise ValueError(f"Unknown AI_PROVIDER: {provider}. Use 'auto', 'groq', 'ollama', or 'claude'")


def call_ai(client, messages, system=None, max_tokens=2000):
    """
    Unified API call that works with any client.
    """
    try:
        if isinstance(client, str):
            # Called with provider name, get client first
            provider, actual_client = client
            client = actual_client

        response = client.create(messages=messages, system=system, max_tokens=max_tokens)
        return response.content[0].text
    except Exception as e:
        print(f"Error calling AI: {e}")
        raise
