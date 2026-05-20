"""
LightRAG with Claude (Anthropic) + Voyage AI embeddings

Requirements:
    pip install lightrag-hku anthropic voyageai

Environment variables needed:
    ANTHROPIC_API_KEY  - from https://console.anthropic.com
    VOYAGE_API_KEY     - from https://dash.voyageai.com  (free tier: 50M tokens/month)
"""

import asyncio
import os
from dotenv import load_dotenv
from lightrag import LightRAG, QueryParam

load_dotenv()

from anthropic import AsyncAnthropic
from lightrag.llm.openai import openai_embed
from lightrag.utils import EmbeddingFunc

_anthropic_client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


async def claude_complete(prompt, system_prompt=None, history_messages=None, **kwargs):
    """Direct Anthropic call returning a plain string (no streaming)."""
    kwargs.pop("hashing_kv", None)
    kwargs.pop("keyword_extraction", None)
    messages = list(history_messages or []) + [{"role": "user", "content": prompt}]
    params = {"model": "claude-sonnet-4-6", "max_tokens": 4096, "messages": messages}
    if system_prompt:
        params["system"] = system_prompt
    response = await _anthropic_client.messages.create(**params)
    return response.content[0].text


async def main():
    rag = LightRAG(
        working_dir="./lightrag_cache",

        # LLM: Claude Sonnet 4.6
        llm_model_func=claude_complete,
        llm_model_name="claude-sonnet-4-6",
        llm_model_max_async=4,
        llm_model_kwargs={"max_tokens": 4096},

        # Embeddings: OpenAI text-embedding-3-small
        embedding_func=EmbeddingFunc(
            embedding_dim=1536,
            max_token_size=8192,
            func=lambda texts: openai_embed(
                texts,
                model="text-embedding-3-small",
                api_key=os.environ.get("OPENAI_API_KEY"),
            ),
        ),
    )

    await rag.initialize_storages()

    # --- Insert transcript files ---
    transcript_dir = os.path.dirname(os.path.abspath(__file__))
    transcripts = [f for f in os.listdir(transcript_dir) if f.endswith(".txt")]

    for filename in transcripts:
        path = os.path.join(transcript_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"\nInserting: {filename} ({len(content)} chars)")
        await rag.ainsert(content)

    # --- Query ---
    question = "how to use chatgpt?"

    print("\n=== hybrid mode ===")
    result = await rag.aquery(question, param=QueryParam(mode="hybrid"))
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
