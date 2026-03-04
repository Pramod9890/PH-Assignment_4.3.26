import os
import requests
from utils.logger import get_logger

try:
    import google.generativeai as genai
except Exception:
    genai = None

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if genai and GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception:
        # configuration failure will be surfaced when calling Gemini
        pass

logger = get_logger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"


class OllamaService:

    @staticmethod
    def ask(question: str, document_text: str) -> dict:
        prompt = f"""
        Answer only from the below context:

        {document_text}

        Question: {question}
        """

        payload = {
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()

        result = response.json()

        return {
            "answer": result.get("response", "").strip(),
            "confidence": "high"
        }


class GeminiService:
    @staticmethod
    def ask_sync(question: str, document_text: str) -> dict:
        if not genai:
            raise RuntimeError("google.generativeai is not available")

        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        try:
            model = genai.GenerativeModel(model_name)
        except Exception as e:
            logger.exception("Failed to initialize Gemini model")
            raise RuntimeError(f"Failed to initialize Gemini model '{model_name}': {e}") from e

        prompt = f"""
        Answer only from the below context:

        {document_text}

        Question: {question}
        """

        try:
            response = model.generate_content(prompt)
        except Exception as e:
            logger.exception("Gemini generate_content failed")
            try:
                from google.api_core import exceptions as google_exceptions
                if isinstance(e, google_exceptions.NotFound):
                    raise RuntimeError(
                        f"Model '{model_name}' not found for the current API version.\n"
                        "Set a supported model in the GEMINI_MODEL env var or list available models via the Google Generative API."
                    ) from e
            except Exception:
                pass
            raise

        # response shape can vary; try common attributes
        text = getattr(response, "text", None)
        if text is None:
            try:
                text = response.candidates[0].content[0].text
            except Exception:
                text = str(response)

        return {
            "answer": text.strip() if isinstance(text, str) else str(text),
            "confidence": "high"
        }
