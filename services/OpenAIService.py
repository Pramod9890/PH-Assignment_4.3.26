import os
import httpx
from utils.logger import get_logger

logger = get_logger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIService:

    @staticmethod
    async def ask(question: str, document_text: str) -> dict:
        prompt = f"""
        Answer only from the below context:

        {document_text}

        Question: {question}
        """

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                OPENAI_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()

        answer = result["choices"][0]["message"]["content"]

        return {
            "answer": answer.strip(),
            "confidence": "high"
        }