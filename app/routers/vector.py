from fastapi import APIRouter, HTTPException
from app.routers import vector_service
from app.models import QueryVector, StackAIError


router = APIRouter()

@router.post("/libraries/{library_id}/search_vectors")
def search_vector_similarities(library_id: int, query: QueryVector):        
    try:
        similar_vectors = vector_service.search_similar_sentences(library_id, query)

        if not similar_vectors:
            raise StackAIError("Library not found", error_code=404)
    
        return similar_vectors
    except Exception as e:
        raise HTTPException(status_code=e.error_code, detail=str(e))    
