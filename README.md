# Ayurveda IPR Assistant (Stage-1 MVP)

A Retrieval-Augmented Generation (RAG) chatbot designed to answer Intellectual Property (IP) questions specific to Ayurveda, with mandatory citations and a formulation classification flow.

## Project Structure
- `ingest.py`: Script to chunk and ingest plain-text documents into ChromaDB.
- `rag.py`: Contains retrieval, reranking, and generation logic using Gemini.
- `classifier.py`: Decision-tree based classification flow for Ayurvedic formulations.
- `api.py`: FastAPI backend exposing chat and classification endpoints.
- `app.py`: Streamlit frontend with a chat interface, jurisdiction toggle, and source tracking.
- `eval/`: Directory containing 25 test questions (`test_questions.json`) and an evaluation script (`eval_script.py`).

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Rename `.env.example` to `.env` and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. **Prepare the Corpus**
   Place your plain-text legal documents in the appropriate folders:
   - `/data/india` (e.g., Patents Act 1970, GI Act)
   - `/data/international` (e.g., TRIPS, CBD, Nagoya Protocol)

4. **Run Ingestion**
   Ingest the documents into the local ChromaDB vector store:
   ```bash
   python ingest.py
   ```

5. **Start the API Server**
   ```bash
   python api.py
   ```
   The API will run on `http://localhost:8000`.

6. **Start the Streamlit UI**
   In a separate terminal, start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Evaluation
To run the evaluation suite and measure answer accuracy, citation correctness, and abstention rate:
```bash
python eval/eval_script.py
```

## Features Implemented
- **Jurisdiction Toggle:** Switch between India and International databases.
- **Formulation Classification:** Interactive sidebar to classify products and explain their IP posture.
- **Mandatory Citations:** Citations generated strictly from retrieved documents.
- **Confidence Indicator:** Color-coded confidence scores based on retrieval similarity.
- **Abstention on Out-of-Scope:** Abstains when confidence is low or when queried with out-of-scope topics.
