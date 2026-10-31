from fastapi import APIRouter, Depends, HTTPException

from app.utils.vector_store import search_query

from app.utils.llm import generate_answer

from app.utils.jwt_handler import get_current_user

from app.models.user import User


router = APIRouter()


MAX_QUERY_LENGTH = 500


@router.get("/chat")
def chat(
    query: str,
    current_user: User = Depends(get_current_user)
):

    if len(query) > MAX_QUERY_LENGTH:

        raise HTTPException(
            status_code=400,
            detail="Question is too long. Keep it under 500 characters."
        )

    results = search_query(query, current_user.email)

    if not results:

        return {
            "query": query,
            "user": current_user.email,
            "answer": "No documents found yet. Add a TXT or PDF first, then ask again.",
            "sources": []
        }

    context = "\n".join(results)

    answer = generate_answer(
        context=context,
        query=query
    )

    return {
        "query": query,
        "user": current_user.email,
        "answer": answer,
        "sources": results
    }
