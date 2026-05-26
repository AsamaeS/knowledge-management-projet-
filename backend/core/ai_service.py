import json
import logging
from typing import List, Dict, Any, Optional
import httpx
from openai import AsyncOpenAI
from backend.config import settings, Settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, config: Settings = settings):
        self.config = config
        self.openai_client = None
        self._local_embedding_model = None

        if self.config.LLM_PROVIDER == "openai" or self.config.EMBEDDING_PROVIDER == "openai":
            if self.config.OPENAI_API_KEY:
                self.openai_client = AsyncOpenAI(api_key=self.config.OPENAI_API_KEY)
            else:
                logger.warning("OPENAI_API_KEY is not configured. AIService might fail.")

    def _get_local_embedding_model(self):
        """Lazy load sentence-transformers model for local embeddings."""
        if self._local_embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                model_name = self.config.EMBEDDING_MODEL or "all-MiniLM-L6-v2"
                logger.info(f"Loading local embedding model: {model_name}")
                self._local_embedding_model = SentenceTransformer(model_name)
            except Exception as e:
                logger.error(f"Failed to load sentence-transformers: {e}")
                raise
        return self._local_embedding_model

    async def embed(self, text: str) -> List[float]:
        """Embed a single string. Returns vector of configured length."""
        vectors = await self.embed_batch([text])
        return vectors[0]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple strings efficiently."""
        if not texts:
            return []

        # Local embeddings using Sentence-Transformers
        if self.config.EMBEDDING_PROVIDER == "local":
            model = self._get_local_embedding_model()
            # sentence-transformers encode is blocking, run in executor or call directly
            import anyio
            embeddings = await anyio.to_thread.run_sync(model.encode, texts)
            # Convert numpy arrays to float lists and pad/truncate to EMBEDDING_DIMENSION if needed
            result = []
            dim = self.config.EMBEDDING_DIMENSION
            for emb in embeddings:
                emb_list = [float(x) for x in emb]
                # Ensure the dimension matches
                if len(emb_list) < dim:
                    emb_list += [0.0] * (dim - len(emb_list))
                elif len(emb_list) > dim:
                    emb_list = emb_list[:dim]
                result.append(emb_list)
            return result

        # OpenAI embeddings
        elif self.config.EMBEDDING_PROVIDER == "openai":
            if not self.openai_client:
                raise ValueError("AsyncOpenAI client not initialized (check API key).")
            response = await self.openai_client.embeddings.create(
                model=self.config.EMBEDDING_MODEL,
                input=texts
            )
            return [data.embedding for data in response.data]

        # Ollama embeddings (via HTTP)
        elif self.config.EMBEDDING_PROVIDER == "ollama":
            url = f"{self.config.OLLAMA_BASE_URL}/api/embeddings"
            results = []
            async with httpx.AsyncClient() as client:
                for text in texts:
                    try:
                        resp = await client.post(
                            url,
                            json={"model": self.config.OLLAMA_MODEL, "prompt": text},
                            timeout=60.0
                        )
                        resp.raise_for_status()
                        emb = resp.json()["embedding"]
                        # Match dimension
                        dim = self.config.EMBEDDING_DIMENSION
                        if len(emb) < dim:
                            emb += [0.0] * (dim - len(emb))
                        elif len(emb) > dim:
                            emb = emb[:dim]
                        results.append(emb)
                    except Exception as e:
                        logger.error(f"Ollama embedding failure: {e}")
                        # Fallback to zero vector
                        results.append([0.0] * self.config.EMBEDDING_DIMENSION)
            return results

        else:
            raise ValueError(f"Unknown EMBEDDING_PROVIDER: {self.config.EMBEDDING_PROVIDER}")

    async def complete(self,
                       messages: List[Dict[str, str]],
                       temperature: float = 0.2,
                       response_format: str = "text") -> str:
        """Call LLM with messages. response_format: 'text' or 'json'."""
        
        # OpenAI LLM
        if self.config.LLM_PROVIDER == "openai":
            if not self.openai_client:
                raise ValueError("AsyncOpenAI client not initialized (check API key).")
            
            kwargs = {
                "model": self.config.OPENAI_MODEL,
                "messages": messages,
                "temperature": temperature
            }
            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}
                
            response = await self.openai_client.chat.completions.create(**kwargs)
            return response.choices[0].message.content

        # Ollama LLM
        elif self.config.LLM_PROVIDER == "ollama":
            url = f"{self.config.OLLAMA_BASE_URL}/api/chat"
            payload = {
                "model": self.config.OLLAMA_MODEL,
                "messages": messages,
                "options": {"temperature": temperature},
                "stream": False
            }
            if response_format == "json":
                payload["format"] = "json"
                
            async with httpx.AsyncClient() as client:
                try:
                    resp = await client.post(url, json=payload, timeout=90.0)
                    resp.raise_for_status()
                    return resp.json()["message"]["content"]
                except Exception as e:
                    logger.error(f"Ollama completion failure: {e}")
                    raise

        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {self.config.LLM_PROVIDER}")

    async def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities and relationships from a text chunk. Returns structured JSON."""
        system_prompt = (
            "You are an AI data architect specialized in knowledge graph construction.\n"
            "Analyze the text provided by the user and extract all key entities and relationships.\n"
            "Deduplicate entities and normalize their labels (e.g. use proper company names like 'Tesla' instead of 'Tesla Inc').\n"
            "Return a JSON object matching this schema exactly:\n"
            "{\n"
            "  \"entities\": [\n"
            "    {\"label\": \"Entity Name\", \"type\": \"person|company|theme|concept|insight\", \"description\": \"Short context description\"}\n"
            "  ],\n"
            "  \"relationships\": [\n"
            "    {\"source\": \"Entity Name A\", \"relation\": \"works_at|mentions|related_to|opposes\", \"target\": \"Entity Name B\", \"weight\": 1.0, \"properties\": {}}\n"
            "  ]\n"
            "}\n"
            "Return only valid JSON. Do not write explanations."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
        
        try:
            content = await self.complete(messages, temperature=0.1, response_format="json")
            return json.loads(content)
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {"entities": [], "relationships": []}

    async def score_simulation_response(self,
                                        step_content: str,
                                        evaluation_criteria: Dict[str, Any],
                                        user_response: str) -> Dict[str, Any]:
        """Score a user's open-text simulation response against the rubric."""
        system_prompt = (
            "You are an expert evaluator assessing a professional simulation interview.\n"
            "Review the scenario step description, evaluation criteria, and the user's raw text response.\n"
            "Score the user's response on content and reasoning (each from 0 to 10), and provide brief qualitative feedback.\n"
            "Return a JSON object matching this schema exactly:\n"
            "{\n"
            "  \"scores\": {\n"
            "    \"content\": 7.5,\n"
            "    \"reasoning\": 8.0,\n"
            "    \"total\": 7.75\n"
            "  },\n"
            "  \"feedback\": \"Your response correctly addresses... however...\"\n"
            "}\n"
            "Return only valid JSON. Do not write explanations."
        )
        
        user_prompt = (
            f"--- SCENARIO STEP CONTENT ---\n{step_content}\n\n"
            f"--- EVALUATION CRITERIA ---\n{json.dumps(evaluation_criteria, indent=2)}\n\n"
            f"--- USER RESPONSE ---\n{user_response}\n"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            content = await self.complete(messages, temperature=0.2, response_format="json")
            return json.loads(content)
        except Exception as e:
            logger.error(f"Simulation scoring failed: {e}")
            return {
                "scores": {"content": 5.0, "reasoning": 5.0, "total": 5.0},
                "feedback": f"System evaluation was skipped due to an error: {str(e)}"
            }
