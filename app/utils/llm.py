import os

import requests


# LLM_PROVIDER=ollama (default, runs on your computer) or groq (hosted, free tier).
PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


SYSTEM_PROMPT = (
    "You answer questions about the user's uploaded documents. "
    "Use only the information provided. "
    "Give a complete answer in 2 to 4 full sentences that includes the key facts "
    "that relate to the question, such as names, roles, companies, dates, degrees and numbers. "
    "Never answer with only a name or a few words. "
    "Do not mention 'the context' or 'the documents'. "
    "If the answer is not in the information provided, reply exactly: "
    "I could not find that in the uploaded documents."
)


def _ask_ollama(messages):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "stream": False,
            "options": {"temperature": 0.3},
            "messages": messages,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()["message"]["content"]


def _ask_groq(messages):

    response = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 400,
        },
        timeout=60,
    )

    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]


def generate_answer(context, query):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Information:\n{context}\n\nQuestion: {query}"
        },
    ]

    if PROVIDER == "groq" and not GROQ_API_KEY:
        return "The answer service is not configured. Set GROQ_API_KEY and try again."

    try:

        if PROVIDER == "groq":
            return _ask_groq(messages)

        return _ask_ollama(messages)

    except requests.exceptions.HTTPError as error:

        if error.response is not None and error.response.status_code == 429:
            return "Too many questions right now. Wait a moment and try again."

        return "The answer service returned an error. Try again."

    except requests.exceptions.RequestException:

        if PROVIDER == "groq":
            return "Cannot reach the answer service. Try again in a moment."

        return "The language model is not reachable. Start Ollama and try again."
