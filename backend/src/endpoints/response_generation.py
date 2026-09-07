from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from services.rag.document_retrieval import queryRetrieval
from schemas.response_generation_valid import QueryRequest

response_generation = APIRouter(prefix="/response_generation", tags=["response_generation"])

@response_generation.post("/answer")
async def answer_endpoint(query: QueryRequest):
    try:
        rag = queryRetrieval()
        stream = rag.answer(query.question)
        return StreamingResponse(stream, media_type="text/plain")

    except HTTPException:
            raise
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
