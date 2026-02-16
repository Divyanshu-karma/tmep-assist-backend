# api.py

import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from src.models.trademark import TrademarkApplication
from src.rag.input_adapter import structured_object_to_query
from src.rag.generate_answer import generate_rag_answer


# -------------------------------------------------
# Logging Setup
# -------------------------------------------------

logging.basicConfig(level=logging.INFO)


# -------------------------------------------------
# Environment Setup
# -------------------------------------------------

TMEP_DOC_VERSION = os.getenv("TMEP_DOC_VERSION")

if not TMEP_DOC_VERSION:
    raise RuntimeError("TMEP_DOC_VERSION environment variable not set.")


# -------------------------------------------------
# FastAPI App
# -------------------------------------------------

app = FastAPI(
    title="TMEP Assist API",
    description="AI-powered Trademark Risk Assessment using RAG + TMEP",
    version="1.0.0"
)


# -------------------------------------------------
# Request Model
# -------------------------------------------------

class TrademarkRequest(BaseModel):
    data: Dict[str, Any]
    doc_version: str


# -------------------------------------------------
# Main Analyze Endpoint
# -------------------------------------------------
@app.get("/")
def root():
    return {"status": "running"}


@app.post("/analyze")
def analyze_trademark(request: TrademarkRequest):

    logging.info("Step 1: Request received")

    try:
        app_obj = TrademarkApplication(request.data)
        logging.info("Step 2: Structured object built")

        query = structured_object_to_query(app_obj)
        logging.info("Step 3: Query constructed")

        result = generate_rag_answer(
            query=query,
            doc_version=request.doc_version,
            top_k=3
        )

        logging.info("Step 4: RAG completed")

        return {
            "status": "success",
            "analysis": result
        }

    except Exception as e:
        logging.error(f"Analyze failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# -------------------------------------------------
# Health Endpoint
# -------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "TMEP Assist API"
    }


# -------------------------------------------------
# Readiness Endpoint (Weaviate Check)
# -------------------------------------------------

@app.get("/ready")
def ready():
    try:
        from src.vectorstore.weaviate_client import get_client
        client = get_client()
        ready_status = client.is_ready()
        client.close()

        return {
            "weaviate_ready": ready_status
        }

    except Exception as e:
        logging.error(f"Weaviate readiness failed: {str(e)}", exc_info=True)
        return {
            "weaviate_ready": False,
            "error": str(e)
        }




# -------------------------------------------------
# Local Run
# -------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)
