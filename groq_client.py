import os
import requests
from typing import Optional

class GroqClient:
    """
    Groq API client for free, ultra-fast inference.
    Sign up free at https://console.groq.com
    """

    def __init__(self, api_key: str = None, model: str = "mixtral-8x7b-32768"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"

        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment")

    def create(self, messages: list, system: Optional[str] = None, max_tokens: int = 2000) -> "GroqResponse":
        """
        Mimic Anthropic API structure for easy migration.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: System prompt
            max_tokens: Max tokens

        Returns: Response object with .content[0].text
        """
        # Build full messages with system prompt
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})

        full_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": full_messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            # Extract text from Groq response
            if "choices" in result and len(result["choices"]) > 0:
                text = result["choices"][0]["message"]["content"]
                return GroqResponse(text)
            else:
                raise RuntimeError(f"Unexpected Groq response: {result}")

        except requests.exceptions.ConnectionError:
            raise RuntimeError("Cannot connect to Groq API. Check internet connection.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise RuntimeError("Invalid GROQ_API_KEY. Check your credentials at https://console.groq.com")
            elif e.response.status_code == 429:
                raise RuntimeError("Groq rate limit exceeded. Wait a moment and retry.")
            else:
                raise RuntimeError(f"Groq API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Groq error: {e}")


class GroqResponse:
    """Mimics Anthropic API response structure."""

    def __init__(self, text: str):
        self.content = [GroqContent(text)]


class GroqContent:
    """Mimics Anthropic API content structure."""

    def __init__(self, text: str):
        self.text = text
