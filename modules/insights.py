"""
Insights module — document comparison, key theme extraction, report generation.
This is what separates VeriDocs from a basic chatbot.
"""
import json
import re
from typing import Any
from modules.chat import _get_model

def extract_themes(chunks: list[dict], source_name: str) -> list[str]:
    """
    Extract 5 key themes/topics from a single document's chunks using Gemini.
    """
    # Grab chunks for this specific document
    doc_chunks = [c["text"] for c in chunks if c.get("source") == source_name]
    
    if not doc_chunks:
        return []
        
    # Concatenate first ~3000 chars to save tokens while capturing the essence
    full_text = "\n".join(doc_chunks)
    text_sample = full_text[:3000]
    
    prompt = (
        f"Analyze the following document excerpt and extract the 5 most important core themes or topics.\n\n"
        f"Document Excerpt:\n{text_sample}\n\n"
        f"Return ONLY a valid JSON array of 5 strings. No markdown formatting like ```json, just the array itself.\n"
        f"Example: [\"Topic 1\", \"Topic 2\", \"Topic 3\", \"Topic 4\", \"Topic 5\"]"
    )
    
    try:
        model = _get_model()
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean up any potential markdown formatting the LLM might hallucinate
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        themes = json.loads(text)
        if isinstance(themes, list):
            return [str(t) for t in themes][:5]
        return []
    except Exception as e:
        # Fallback if Gemini fails or returns malformed JSON
        return ["Error extracting themes"]


def compare_documents(chunks: list[dict]) -> dict:
    """
    Compare chunks across 2+ documents. Find agreements, contradictions, gaps.
    
    Returns:
        {
            "agreements": list[str],
            "contradictions": list[str],
            "unique_to": {filename: list[str]},
            "summary": str
        }
    """
    from collections import defaultdict
    doc_map = defaultdict(list)
    for c in chunks:
        doc_map[c.get("source", "Unknown")].append(c["text"])
        
    if len(doc_map) < 2:
        return {
            "agreements": [],
            "contradictions": [],
            "unique_to": {},
            "summary": "Need at least 2 documents to perform a comparison."
        }
        
    # Build excerpts for comparison (e.g. first 2000 chars of each doc)
    comparison_text = ""
    filenames = []
    for doc_name, doc_texts in doc_map.items():
        excerpt = "\n".join(doc_texts)[:2000]
        comparison_text += f"\n--- Document: {doc_name} ---\n{excerpt}\n"
        filenames.append(doc_name)
        
    json_schema = '''{
    "agreements": ["point 1", "point 2"],
    "contradictions": ["point 1 vs point 2"],
    "unique_to": {"doc1.pdf": ["unique point"], "doc2.pdf": []},
    "summary": "overall summary"
}'''

    prompt = (
        f"Compare the following document excerpts. Identify agreements, contradictions, and unique points.\n"
        f"Documents:\n{comparison_text}\n\n"
        f"Return ONLY valid JSON matching this exact schema: {json_schema}\n"
        f"No markdown blocks, just raw JSON."
    )
    
    try:
        model = _get_model()
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
             text = text[7:]
        if text.startswith("```"):
             text = text[3:]
        if text.endswith("```"):
             text = text[:-3]
        text = text.strip()
        
        data = json.loads(text)
        # Ensure correct structure
        return {
            "agreements": data.get("agreements", []),
            "contradictions": data.get("contradictions", []),
            "unique_to": data.get("unique_to", {f: [] for f in filenames}),
            "summary": data.get("summary", "")
        }
    except Exception as e:
        return {
            "agreements": [],
            "contradictions": [],
            "unique_to": {f: [] for f in filenames},
            "summary": "Error generating comparison."
        }


def generate_report(
    query_history: list[dict],
    comparison: dict,
    themes: dict
) -> str:
    """
    Generate a Markdown report summarising the session.
    """
    md = ["# VeriDocs Session Report", ""]
    
    md.append("## Overview")
    if comparison and "summary" in comparison:
        md.append(comparison["summary"])
    md.append("")
    
    md.append("## Themes by Document")
    for doc, doc_themes in themes.items():
        md.append(f"### {doc}")
        if doc_themes:
            for t in doc_themes:
                md.append(f"- {t}")
        else:
             md.append("- No themes extracted.")
        md.append("")
        
    md.append("## Cross-Document Comparison")
    if comparison:
        agreements = comparison.get("agreements", [])
        if agreements:
            md.append("### Key Agreements")
            for a in agreements:
                md.append(f"- {a}")
            md.append("")
            
        contradictions = comparison.get("contradictions", [])
        if contradictions:
            md.append("### Contradictions / Conflicts")
            for c in contradictions:
                md.append(f"- {c}")
            md.append("")
            
        unique = comparison.get("unique_to", {})
        if any(unique.values()):
            md.append("### Unique Content")
            for doc, points in unique.items():
                if points:
                    md.append(f"**{doc}**")
                    for p in points:
                        md.append(f"- {p}")
            md.append("")
        
    if query_history:
        md.append("## Q&A Session History")
        for i, qna in enumerate(query_history, 1):
            md.append(f"**Q{i}:** {qna.get('query', '')}")
            md.append(f"**A{i}:** {qna.get('answer', '')}")
            citations = qna.get('citations', [])
            if citations:
                cites = [f"*{c['source']} (p.{c['page']})*" for c in citations]
                md.append(f"*Sources:* {', '.join(cites)}")
            md.append("")
            
    return "\n".join(md)
