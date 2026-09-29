import os
import re
import uuid
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

# Initialize ChromaDB client (persistent)
client = chromadb.PersistentClient(path="./chroma_db")

# Use multilingual-e5-base via sentence-transformers
model = SentenceTransformer('intfloat/multilingual-e5-base')

def get_or_create_collection(name="ayurveda_ipr"):
    # Create a collection with cosine similarity
    try:
        collection = client.get_collection(name=name)
    except Exception:
        collection = client.create_collection(name=name, metadata={"hnsw:space": "cosine"})
    return collection

def chunk_by_section(text: str, filename: str) -> List[Dict[str, Any]]:
    """
    Chunks text based on Section, Article, or Rule.
    If it doesn't match these patterns, falls back to paragraph splitting.
    """
    chunks = []
    
    # Regex to match Section, Article, or Rule, e.g., "Section 3(p)" or "Article 15"
    # It splits text such that the delimiter is kept (using lookahead or manual attachment)
    pattern = r"(?=(?:Section|Article|Rule)\s+\d+[a-zA-Z0-9\(\)]*)"
    
    parts = re.split(pattern, text, flags=re.IGNORECASE)
    
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
            
        # Try to extract the specific section/article number
        match = re.match(r"(Section|Article|Rule)\s+(\d+[a-zA-Z0-9\(\)]*)", part, re.IGNORECASE)
        section_name = f"{match.group(1)} {match.group(2)}" if match else f"Chunk {i}"
        
        chunks.append({
            "text": part,
            "section": section_name
        })
        
    return chunks

def ingest_directory(directory: str, jurisdiction: str, version: str = "1.0"):
    collection = get_or_create_collection()
    
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist. Skipping.")
        return

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath):
            continue
            
        print(f"Ingesting {filename}...")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue
            
        chunks = chunk_by_section(content, filename)
        
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            # For multilingual-e5, prefix queries with "query: " and passages with "passage: "
            # However, during ingestion, we just embed as "passage: "
            text = chunk["text"]
            if not text.strip():
                continue
                
            passage = f"passage: {text}"
            
            # We don't embed here if we let chromadb do it, but we are using our own model.
            # We will compute embeddings manually and pass to chroma.
            
            metadata = {
                "jurisdiction": jurisdiction,
                "source_name": filename,
                "section": chunk["section"],
                "doc_version": version,
                "date": "2024-01-01" # Default or extract from somewhere
            }
            
            documents.append(text)
            metadatas.append(metadata)
            ids.append(str(uuid.uuid4()))
            
        if documents:
            # Generate embeddings
            embeddings = model.encode([f"passage: {doc}" for doc in documents]).tolist()
            
            # Upsert into Chroma
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Added {len(documents)} chunks from {filename}")

if __name__ == "__main__":
    print("Starting ingestion...")
    ingest_directory("data/india", "India")
    ingest_directory("data/international", "International")
    print("Ingestion complete.")
