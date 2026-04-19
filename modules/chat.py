"""
Chat module — Gemini Flash API for answering questions with context.
Formats retrieved chunks into a prompt, returns answer + citations.
"""
import os
from typing import Any
import google.generativeai as genai


SYSTEM_PROMPT = """You are VeriDocs, an intelligent document analysis assistant.
You answer questions strictly based on the provided document context.
Always cite your sources by mentioning the document name and page number.
If the answer is not in the context, say so clearly — do not hallucinate.
Be concise, structured, and precise."""

# We'll instantiate the model lazily or just cache it
_model = None

def _get_model():
    """Configure and return the Gemini GenerativeModel singleton."""
    global _model
    if _model is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            # Don't strictly fail on import so tests can be mocked, but log/warn if actually used
            pass
        else:
            genai.configure(api_key=api_key)
            
        # Using Google's system_instruction param explicitly for 1.5 flash
        _model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
    return _model


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
    
    prompt = (
        "CONTEXT:\n"
        f"{full_context}\n\n"
        "QUESTION:\n"
        f"{query}"
    )
    return prompt


def ask(query: str, retrieved_chunks: list[dict]) -> dict:
    """
    Send prompt to Gemini Flash and return structured response.
    
    Returns:
        {
            "answer": str,
            "citations": list[{"source": str, "page": int}],
            "model": str
        }
    """
    prompt = build_context_prompt(query, retrieved_chunks)
    model = _get_model()
    
    response = model.generate_content(prompt)
    answer_text = response.text if response else "No response generated."
    
    # Provide the chunks used as citations (removing duplicates)
    citations = []
    seen = set()
    for chunk in retrieved_chunks:
        src = chunk.get("source", "Unknown")
        pg = chunk.get("page", 1)
        key = (src, pg)
        if key not in seen:
            citations.append({"source": src, "page": pg})
            seen.add(key)
            
    return {
        "answer": answer_text.strip(),
        "citations": citations,
        "model": "gemini-1.5-flash"
    }
