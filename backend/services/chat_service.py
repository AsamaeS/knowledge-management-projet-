import logging
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

# Models & Schemas
from backend.schemas.chat import ChatMessageRequest, ChatMessageResponse, Citation, StatementLabel
from backend.services.retrieval_service import RetrievalService
from backend.core.ai_service import AIService

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, db: AsyncSession, ai_service: AIService):
        self.db = db
        self.ai_service = ai_service
        self.retrieval_service = RetrievalService(db, ai_service)

    async def answer(self, request: ChatMessageRequest) -> ChatMessageResponse:
        """Runs the semantic retrieval, builds the system prompt, invokes LLM, and parses answers."""
        query = request.message
        output_format = request.output_format or "text"

        logger.info(f"ChatService processing message: {query} (format: {output_format})")

        # 1. Retrieve Semantics (Chunks + Nodes)
        matched_chunks = await self.retrieval_service.search_chunks(query, limit=8)
        matched_nodes = await self.retrieval_service.search_nodes(query, limit=5)

        # 2. Assemble Context
        context_chunks_str = ""
        context_nodes_str = ""

        # Tracking dictionary to map filenames/types back to UUIDs for citation extraction
        provenance_map = {}

        for i, (chunk, doc) in enumerate(matched_chunks):
            ref_name = doc.filename.strip()
            # Register in provenance map
            provenance_key = f"{ref_name.lower()}:{doc.source_type.lower()}"
            provenance_map[provenance_key] = {
                "chunk_id": chunk.id,
                "document_id": doc.id,
                "filename": doc.filename,
                "source_type": doc.source_type,
                "content": chunk.content
            }
            context_chunks_str += (
                f"--- CHUNK {i+1} ---\n"
                f"Source: {doc.filename}\n"
                f"Type: {doc.source_type}\n"
                f"Content: {chunk.content}\n\n"
            )

        for i, node in enumerate(matched_nodes):
            context_nodes_str += (
                f"- Entity: {node.label} (Type: {node.type})\n"
                f"  Description: {node.description or 'N/A'}\n"
            )

        # 3. Create System Prompt
        system_instructions = (
            "You are NEXUS, an expert AI analyst specialized in the automotive industry.\n"
            "You answer questions based ONLY on the provided knowledge base context.\n"
            "Always cite your sources using the EXACT inline format: [SOURCE: filename, type] (do not change the filename or type).\n"
            "Clearly label each statement or paragraph using prefix tags:\n"
            "  [FACT] — directly stated in a source document\n"
            "  [OPINION] — an expert's stated view from the corpus\n"
            "  [INFERENCE] — your reasoned conclusion from multiple sources\n\n"
            "If information is not in the context, say so explicitly — do not hallucinate.\n\n"
            "--- CONTEXT CHUNKS ---\n"
            f"{context_chunks_str}\n"
            "--- CONTEXT KNOWLEDGE GRAPH ENTITIES ---\n"
            f"{context_nodes_str}\n"
        )

        if output_format == "swot":
            system_instructions += (
                "You MUST return a JSON object matching this schema exactly:\n"
                "{\n"
                "  \"strengths\": [\"[FACT] Strength text [SOURCE: filename, type]\", ...],\n"
                "  \"weaknesses\": [\"[OPINION] Weakness text [SOURCE: filename, type]\", ...],\n"
                "  \"opportunities\": [\"[INFERENCE] Opportunity text [SOURCE: filename, type]\", ...],\n"
                "  \"threats\": [\"[INFERENCE] Threat text [SOURCE: filename, type]\", ...]\n"
                "}\n"
                "Format the answers inside arrays with appropriate FACT/OPINION/INFERENCE labels and source citations.\n"
                "Return only valid JSON."
            )
        elif output_format == "pestel":
            system_instructions += (
                "You MUST return a JSON object matching this schema exactly:\n"
                "{\n"
                "  \"political\": [\"[FACT] Text [SOURCE: filename, type]\", ...],\n"
                "  \"economic\": [\"[FACT] Text [SOURCE: filename, type]\", ...],\n"
                "  \"social\": [\"[FACT] Text [SOURCE: filename, type]\", ...],\n"
                "  \"technological\": [\"[FACT] Text [SOURCE: filename, type]\", ...],\n"
                "  \"environmental\": [\"[FACT] Text [SOURCE: filename, type]\", ...],\n"
                "  \"legal\": [\"[FACT] Text [SOURCE: filename, type]\", ...]\n"
                "}\n"
                "Format the answers inside arrays with appropriate FACT/OPINION/INFERENCE labels and source citations.\n"
                "Return only valid JSON."
            )
        else:
            system_instructions += (
                "Provide a detailed plain markdown analysis. Format your paragraphs or lists clearly, prefixing segments with "
                "[FACT], [OPINION], or [INFERENCE] and including inline citations like [SOURCE: filename, type]."
            )

        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": query}
        ]

        # 4. Invoke LLM
        response_format_arg = "json" if output_format in ["swot", "pestel"] else "text"
        try:
            llm_content = await self.ai_service.complete(
                messages=messages,
                temperature=0.2,
                response_format=response_format_arg
            )
        except Exception as e:
            logger.error(f"LLM Chat invocation failed: {e}")
            return ChatMessageResponse(
                answer="Failed to get response from AI. Please try again.",
                citations=[],
                output_type=output_format,
                confidence=0.0,
                fact_vs_opinion_labels=[]
            )

        # 5. Extract Citations and Labels
        extracted_citations = []
        fact_opinion_labels = []
        final_answer = llm_content

        # Extract citations using regex search: [SOURCE: filename, type]
        # Match pattern: \[SOURCE:\s*([^,\]]+),\s*([^\]]+)\]
        citation_matches = re.findall(r"\[SOURCE:\s*([^,\]]+),\s*([^\]]+)\]", llm_content, re.IGNORECASE)
        
        # Unique citations set to avoid duplicate entries in list
        unique_citations = set()

        for filename_match, type_match in citation_matches:
            filename_match = filename_match.strip()
            type_match = type_match.strip()
            key = f"{filename_match.lower()}:{type_match.lower()}"
            
            if key in provenance_map and key not in unique_citations:
                unique_citations.add(key)
                prov = provenance_map[key]
                extracted_citations.append(Citation(
                    chunk_id=prov["chunk_id"],
                    document_id=prov["document_id"],
                    filename=prov["filename"],
                    source_type=prov["source_type"],
                    excerpt=prov["content"][:250] + "..." # short excerpt
                ))

        # Parse FACT, OPINION, INFERENCE statements
        # Regex to capture [LABEL] followed by text
        tag_pattern = r"\[(FACT|OPINION|INFERENCE)\]\s*([^\[\n]+)"
        statement_matches = re.finditer(tag_pattern, llm_content, re.IGNORECASE)
        
        for match in statement_matches:
            lbl_type = match.group(1).upper()
            text_snippet = match.group(2).strip()
            # Clean up trailing citations inside the statement text
            text_snippet = re.sub(r"\[SOURCE:[^\]]+\]", "", text_snippet).strip()
            
            if text_snippet:
                fact_opinion_labels.append(StatementLabel(
                    text=text_snippet,
                    label=lbl_type.lower()
                ))

        # If empty structure, do a sentence fallback parsing
        if not fact_opinion_labels and output_format == "text":
            sentences = re.split(r"(?<=[.!?])\s+", llm_content)
            for s in sentences:
                if not s.strip():
                    continue
                clean_s = re.sub(r"\[SOURCE:[^\]]+\]", "", s).strip()
                if "fact" in s.lower():
                    lbl = "fact"
                elif "opinion" in s.lower():
                    lbl = "opinion"
                else:
                    lbl = "inference"
                fact_opinion_labels.append(StatementLabel(text=clean_s, label=lbl))

        # Calculate a mock confidence score based on citations quantity (scale 0 to 1)
        confidence_val = min(0.5 + (len(extracted_citations) * 0.1), 1.0)

        return ChatMessageResponse(
            answer=final_answer,
            citations=extracted_citations,
            output_type=output_format,
            confidence=confidence_val,
            fact_vs_opinion_labels=fact_opinion_labels
        )
