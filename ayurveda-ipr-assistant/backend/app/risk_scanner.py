import json
import os
from rag import retrieve_context, llm

CASE_STUDIES_PATH = os.path.join(os.path.dirname(__file__), "../data/case_studies.json")
try:
    with open(CASE_STUDIES_PATH, "r") as f:
        case_studies = json.load(f)
except Exception:
    case_studies = []

def scan_ingredient_risk(description: str) -> dict:
    docs_india, conf_india = retrieve_context(description, "India", top_k=3)
    docs_intl, conf_intl = retrieve_context(description, "International", top_k=3)
    docs = docs_india + docs_intl
    
    if not docs:
        return {
            "risk_level": "Unknown",
            "explanation": "No relevant traditional knowledge or legal context found in the database. Please consult the TKDL directly for a definitive prior-art search.",
            "matched_sources": [],
            "confidence": "Low",
            "related_case_study": None
        }
        
    context_str = "\n".join([d['text'] for d in docs])
    
    prompt = f"""
    Based ONLY on the retrieved traditional knowledge and legal context below, classify the patentability risk of the following Ayurvedic formulation.
    
    Formulation Description: {description}
    
    Context:
    {context_str}
    
    You must classify the risk into ONE of these exactly:
    - High Risk (matches known traditional knowledge / classical formulation, not patentable under Section 3(p))
    - Medium Risk (partial match, some traditional basis but specific combination might be novel)
    - Low Risk (appears to have no strong traditional knowledge match, potentially patentable pending prior art search)
    
    Respond in strict JSON format EXACTLY like this (no markdown block):
    {{
        "risk_level": "High Risk",
        "explanation": "Brief reasoning",
        "confidence": "High"
    }}
    """
    
    try:
        response = llm.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        result = json.loads(text)
    except Exception as e:
        result = {
            "risk_level": "Unknown",
            "explanation": "Failed to analyze risk with LLM.",
            "confidence": "Low"
        }
        
    matched_sources = []
    for doc in docs:
        meta = doc['metadata']
        matched_sources.append(f"{meta.get('source_name', '')} - {meta.get('section', '')}")
    result["matched_sources"] = list(set(matched_sources))
    
    desc_lower = description.lower()
    related_case = None
    for case in case_studies:
        if case["ingredient"].lower() in desc_lower:
            related_case = case
            break
            
    result["related_case_study"] = related_case
    
    return result
