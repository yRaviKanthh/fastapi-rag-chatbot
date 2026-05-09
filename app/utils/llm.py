import requests


def generate_answer(context, query):

    prompt = f"""
    Context:
    {context}

    Question:
    {query}

    Answer based only on the context above.
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    data = response.json()

    return data["response"]