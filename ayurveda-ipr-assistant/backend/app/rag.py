import os
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# We use gemini-1.5-flash or gemini-1.5-pro
# The user specified Gemini API with a strict system prompt.
generation_config = {
    "temperature": 0.0, # low temperature for factual answers
}

from config import GEMINI_MODEL_NAME

system_instruction = (
    "You are an Ayurveda IPR Assistant. "
    "Answer ONLY from the provided context. Cite every claim by referencing the source exactly as provided in the metadata (Act + section / rule / treaty article / document name). "
    "If the context is insufficient to answer the question, you MUST abstain and say you don't know. "
    "NEVER invent section numbers, treaties, or legal facts. "
    "If a citation is not in the retrieved context, don't output it."
)

model_name = GEMINI_MODEL_NAME

try:
    llm = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        system_instruction=system_instruction
    )
except Exception:
    # Fallback if system_instruction is not supported in the library version
    llm = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config
    )

# Initialize ChromaDB client (persistent)
client = chromadb.PersistentClient(path="./chroma_db")

try:
    collection = client.get_collection(name="ayurveda_ipr")
except Exception:
    collection = client.get_or_create_collection(name="ayurveda_ipr")

# Initialize Embedding Model
embedder = SentenceTransformer('intfloat/multilingual-e5-base')

def retrieve_context(query: str, jurisdiction: str, top_k: int = 5) -> Tuple[List[Dict[str, Any]], str]:
    """
    Retrieves context from ChromaDB based on the query and jurisdiction.
    Returns a tuple of (retrieved_docs, confidence_level).
    """
    # E5 requires "query: " prefix
    query_embedding = embedder.encode(f"query: {query}").tolist()
    
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"jurisdiction": jurisdiction}
        )
    except Exception as e:
        print(f"Error querying ChromaDB: {e}")
        return [], "Low"
    
    docs = []
    if not results['documents'] or not results['documents'][0]:
        return [], "Low"
        
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0] # Cosine distance
    
    for doc, meta, dist in zip(documents, metadatas, distances):
        # Convert distance to similarity (rough proxy)
        similarity = 1.0 - (dist / 2.0) if dist <= 2.0 else 0.0
        
        docs.append({
            "text": doc,
            "metadata": meta,
            "similarity": similarity
        })
        
    # Determine confidence based on top similarity
    top_similarity = docs[0]["similarity"] if docs else 0.0
    
    if top_similarity > 0.85:
        confidence = "High"
    elif top_similarity > 0.70:
        confidence = "Medium"
    else:
        confidence = "Low"
        
    return docs, confidence

def format_context(docs: List[Dict[str, Any]]) -> str:
    formatted = []
    for i, doc in enumerate(docs):
        meta = doc['metadata']
        source = meta.get('source_name', 'Unknown')
        section = meta.get('section', 'Unknown')
        text = doc['text']
        formatted.append(f"--- Document {i+1} ---\nSource: {source}\nSection: {section}\nText: {text}\n")
    return "\n".join(formatted)

def generate_answer(query: str, jurisdiction: str, simplicity_mode: str = "technical") -> Dict[str, Any]:
    docs, confidence = retrieve_context(query, jurisdiction)
    
    if confidence == "Low" or not docs:
        return {
            "answer": "I do not have sufficient context to answer this question with confidence.",
            "confidence": "Low",
            "citations": [],
            "docs": docs
        }
        
    context_str = format_context(docs)
    
    if simplicity_mode == "simple":
        active_instruction = "Explain this in plain, simple Hindi-English mixed language (Hinglish) as if talking to a small Ayurveda practitioner or MSME owner with no legal background. Avoid legal jargon; use everyday words and short sentences. Still cite the source but explain what it means in plain terms. " + system_instruction
    else:
        active_instruction = system_instruction
    
    prompt = (
        f"{active_instruction}\n\n"
        f"Context:\n{context_str}\n\n"
        f"Question: {query}\n"
        f"Answer:"
    )
    
    try:
        response = llm.generate_content(prompt)
        answer = response.text
    except Exception as e:
        answer = f"Error generating answer: {e}"
        confidence = "Low"
        
    citations = []
    for doc in docs:
        meta = doc['metadata']
        citations.append(f"{meta.get('source_name', '')} - {meta.get('section', '')}")
        
    citations = list(set(citations))
        
    return {
        "answer": answer,
        "confidence": confidence,
        "citations": citations,
        "docs": docs
    }

if __name__ == "__main__":
    print(generate_answer("What is section 3(p)?", "India"))
