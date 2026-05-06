"""
Chat module — Groq API for answering questions with context.
Formats retrieved chunks into a prompt, returns answer + citations.
"""
import os
import time
from groq import Groq

SYSTEM_PROMPT = """You are VeriDocs, an intelligent document analysis assistant.
You answer questions strictly based on the provided document context.
Always cite your sources by mentioning the document name and page number.
If the answer is not in the context, say so clearly — do not hallucinate.
Be concise, structured, and precise."""

# Global client singleton
_client = None

def _get_client():
    """Configure and return the Groq client singleton."""
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            # Fallback for environment setup
            return None
        _client = Groq(api_key=api_key)
    return _client


def build_context_prompt(query: str, retrieved_chunks: list[dict]) -> str:
    """
    Build a formatted prompt from query + retrieved chunks.
    Each chunk displays: [Source: filename, Page: N] followed by text.
    """
    if not retrieved_chunks:
         return f"CONTEXT:\nNo documents have been indexed or retrieved.\n\nQUESTION:\n{query}"

    context_blocks = []
    for chunk in retrieved_chunks:
        source = chunk.get("source", "Unknown")
        page   = chunk.get("page", 1)
        text   = chunk.get("text", "").strip()
        
        block = f"[Source: {source}, Page: {page}]\n{text}"
        context_blocks.append(block)

    full_context = "\n\n".join(context_blocks)
    return f"CONTEXT:\n{full_context}\n\nQUESTION: {query}"


def ask(query: str, retrieved_chunks: list[dict]) -> dict:
    """
    Send prompt to Groq with retry logic and return structured response.
    """
    client = _get_client()
    if not client:
        return {
            "answer": "Groq API key not configured.",
            "citations": [],
            "model": "llama-3.1-8b-instant",
            "error": True
        }

    prompt = build_context_prompt(query, retrieved_chunks)

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1024,
            )
            answer = response.choices[0].message.content
            
            # Provide the chunks used as citations (removing duplicates)
            citations = list({
                (c.get("source", "Unknown"), c.get("page", 1))
                for c in retrieved_chunks
            })
            
            return {
                "answer": answer.strip() if answer else "No response generated.",
                "citations": [{"source": s, "page": p} for s, p in citations],
                "model": "llama-3.1-8b-instant",
                "error": False
            }
        except Exception as e:
            error_msg = str(e).lower()
            if "rate" in error_msg and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            
            return {
                "answer": "Something went wrong. Please try again.",
                "citations": [],
                "model": "llama-3.1-8b-instant",
                "error": True
            }
