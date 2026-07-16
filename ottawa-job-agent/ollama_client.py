import requests
import json
from typing import Optional

class OllamaClient:
    """
    Simple wrapper for Ollama API.
    Requires: ollama pull llama3.1:8b (or mistral, etc.)
    Start server: ollama serve
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b"):
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
        full_prompt = f"{system}\n\n{prompt}" if system else prompt

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
