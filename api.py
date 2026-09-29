from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag import generate_answer
from classifier import FormulationClassifier

app = FastAPI(title="Ayurveda IPR Assistant API")
classifier = FormulationClassifier()

class QueryRequest(BaseModel):
    query: str
    jurisdiction: str

class ClassificationRequest(BaseModel):
    node_id: str = "q1"

@app.post("/chat")
def chat_endpoint(request: QueryRequest):
    if request.jurisdiction not in ["India", "International"]:
        raise HTTPException(status_code=400, detail="Invalid jurisdiction")
        
    result = generate_answer(request.query, request.jurisdiction)
    return result

@app.post("/classify")
def classify_endpoint(request: ClassificationRequest):
    node = classifier.get_node(request.node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
