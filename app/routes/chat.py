from fastapi import APIRouter, Depends

from app.utils.vector_store import search_query

from app.utils.llm import generate_answer

from app.utils.jwt_handler import get_current_user

from app.models.user import User


router = APIRouter()


@router.get("/chat")
def chat(
    query: str,
    current_user: User = Depends(get_current_user)
):

    results = search_query(query)

    if not results:

        return {
            "query": query,
            "answer": "No relevant information found in uploaded documents.",
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