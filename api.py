# api.py

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from dotenv import load_dotenv

from src.models.trademark import TrademarkApplication
from src.rag.input_adapter import structured_object_to_query
from src.rag.generate_answer import generate_rag_answer


# -------------------------------------------------
# Environment Setup
# -------------------------------------------------

TMEP_DOC_VERSION = os.getenv("TMEP_DOC_VERSION")

if not TMEP_DOC_VERSION:
    raise RuntimeError("TMEP_DOC_VERSION environment variable not set.")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)


# -------------------------------------------------
# FastAPI App
# -------------------------------------------------

app = FastAPI(
    title="TMEP Assist API",
    description="AI-powered Trademark Risk Assessment using RAG + TMEP",
    version="1.0.0"
)


class TrademarkRequest(BaseModel):
    data: Dict[str, Any]
    doc_version: str


@app.post("/analyze")
def analyze_trademark(request: TrademarkRequest):
    try:
        # Step 1: Convert JSON → structured object
        app_obj = TrademarkApplication(request.data)

        # Step 2: Structured object → deterministic query
        query = structured_object_to_query(app_obj)

        # Step 3: Generate grounded + risk-classified analysis
        result = generate_rag_answer(
            query=query,
            doc_version=request.doc_version    
            top_k=3
        )

        return {
            "status": "success",
            "analysis": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# api.py

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import Dict, Any

# from src.models.trademark import TrademarkApplication
# from src.rag.input_adapter import structured_object_to_query
# from src.rag.generate_answer import generate_rag_answer

# app = FastAPI(
#     title="TMEP Assist API",
#     description="AI-powered Trademark Risk Assessment using RAG + TMEP",
#     version="1.0.0"
# )


# class TrademarkRequest(BaseModel):
#     data: Dict[str, Any]


# @app.post("/analyze")
# def analyze_trademark(request: TrademarkRequest):

#     try:
#         # Convert JSON → structured object
#         app_obj = TrademarkApplication(request.data)

#         # Convert structured object → deterministic query
#         query = structured_object_to_query(app_obj)

#         # Generate RAG answer
       
#         result = generate_rag_answer(
#             query=query,
#             doc_version=TMEP_DOC_VERSION,
#             top_k=3
#         )


#         return {
#             "status": "success",
#             "analysis": result
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
