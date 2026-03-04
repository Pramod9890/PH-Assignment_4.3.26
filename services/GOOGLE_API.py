import os
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)


class GeminiService:

    @staticmethod
    def ask_sync(question: str, document_text: str) -> dict:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        Answer only from the below context:

        {document_text}

        Question: {question}
        """

        response = model.generate_content(prompt)

        return {
            "answer": response.text.strip(),
            "confidence": "high"
        }