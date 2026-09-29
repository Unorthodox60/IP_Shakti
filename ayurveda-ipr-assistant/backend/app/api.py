from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag import generate_answer
from classifier import FormulationClassifier
from risk_scanner import scan_ingredient_risk

app = FastAPI(title="Ayurveda IPR Assistant API")
classifier = FormulationClassifier()

class QueryRequest(BaseModel):
    query: str
    jurisdiction: str
    simplicity_mode: str = "technical"

class ClassificationRequest(BaseModel):
    node_id: str = "q1"

class RiskRequest(BaseModel):
    description: str

@app.post("/chat")
def chat_endpoint(request: QueryRequest):
    if request.jurisdiction not in ["India", "International"]:
        raise HTTPException(status_code=400, detail="Invalid jurisdiction")
        
    result = generate_answer(request.query, request.jurisdiction, request.simplicity_mode)
    return result

@app.post("/classify")
def classify_endpoint(request: ClassificationRequest):
    node = classifier.get_node(request.node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@app.post("/scan-risk")
def scan_risk_endpoint(request: RiskRequest):
    result = scan_ingredient_risk(request.description)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
