import os
import json
import logging
from typing import List

# Optional imports – they may not be installed yet; we import lazily

_logger = logging.getLogger(__name__)

class AIService:
    """Simple wrapper handling embeddings and chat completions.
    Supports OpenAI (default) or Ollama via HTTP.
    """
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "openai").lower()
        if self.provider == "openai":
            try:
                import openai
                self.openai = openai
                self.openai.api_key = os.getenv("OPENAI_API_KEY")
                self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
                self.completion_model = os.getenv("COMPLETION_MODEL", "gpt-4o-mini")
            except Exception as e:
                _logger.error("OpenAI SDK not available: %s", e)
                raise
        else:
            # Ollama – use httpx for async HTTP calls
            import httpx
            self.httpx = httpx
            self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            self.embedding_model = os.getenv("EMBEDDING_MODEL", "mxbai-embed-large")
            self.completion_model = os.getenv("COMPLETION_MODEL", "llama3")

    def get_embedding(self, text: str) -> List[float]:
        """Return embedding vector for the given text.
        Synchronous for simplicity.
        """
        if self.provider == "openai":
            resp = self.openai.embeddings.create(input=text, model=self.embedding_model)
            return resp.data[0].embedding
        else:
            # Ollama embeddings endpoint
            payload = {"model": self.embedding_model, "prompt": text}
            r = self.httpx.post(f"{self.base_url}/api/embeddings", json=payload, timeout=30)
            r.raise_for_status()
            data = r.json()
            return data.get("embedding")

    def generate(self, prompt: str) -> str:
        """Generate a response from the LLM using the given prompt."""
        if self.provider == "openai":
            resp = self.openai.ChatCompletion.create(
                model=self.completion_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return resp.choices[0].message.content.strip()
        else:
            payload = {
                "model": self.completion_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
            r = self.httpx.post(f"{self.base_url}/api/chat", json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            # Ollama returns {"message": {"content": "..."}}
            return data.get("message", {}).get("content", "").strip()
