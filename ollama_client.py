import requests
import json
from typing import Optional

class OllamaClient:
    """
    Simple wrapper for Ollama API.
    Requires: ollama pull mistral (or llama2, neural-chat, etc.)
    Start server: ollama serve
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        self.base_url = base_url
        self.model = model
        self.endpoint = f"{base_url}/api/generate"

    def generate(self, prompt: str, system: Optional[str] = None, max_tokens: int = 2000) -> str:
        """
        Generate text using Ollama.

        Args:
            prompt: User message
            system: System prompt (optional)
            max_tokens: Maximum tokens to generate

        Returns: Generated text
        """
        # Combine system + prompt
        full_prompt = ""
        if system:
            full_prompt = f"{system}\n\n{prompt}"
        else:
            full_prompt = prompt

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "num_predict": max_tokens,
        }

        try:
            response = requests.post(self.endpoint, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: `ollama serve`"
            )
        except Exception as e:
            raise RuntimeError(f"Ollama error: {e}")

    def create(self, messages: list, system: Optional[str] = None, max_tokens: int = 2000) -> "Message":
        """
        Mimic Anthropic API structure for easy migration.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: System prompt
            max_tokens: Max tokens

        Returns: Response object with .content[0].text
        """
        # Extract user message (last one)
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        response_text = self.generate(user_message, system, max_tokens)

        # Return object that mimics Anthropic response
        return OllamaResponse(response_text)


class OllamaResponse:
    """Mimics Anthropic API response structure."""

    def __init__(self, text: str):
        self.content = [OllamaContent(text)]


class OllamaContent:
    """Mimics Anthropic API content structure."""

    def __init__(self, text: str):
        self.text = text
