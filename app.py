import os
from dotenv import load_dotenv
load_dotenv("Environment.env") # loads ./ .env file (or change to "environment.env")

# ...existing code...
from flask import Flask, render_template, request
from services.OpenAIService import OpenAIService
from services.document_service import DocumentService
from services.ai_service import OllamaService, GeminiService
from storage.document_store import document_store
from utils.logger import get_logger

print("API KEY:", os.getenv("GOOGLE_API_KEY"))

logger = get_logger(__name__)
app = Flask(__name__)

AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")  # ollama | openai | gemini
print("AI_PROVIDER:", AI_PROVIDER)
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    try:
        if "file" not in request.files:
            logger.error("No file part in request")
            return render_template("index.html", error="No file uploaded")

        file = request.files["file"]
        if file.filename == "":
            logger.error("No file selected")
            return render_template("index.html", error="No file selected")

        document_id = DocumentService.process_file_sync(file)
        return render_template("index.html", document_id=document_id)

    except Exception as e:
        logger.exception("Upload failed")
        return render_template("index.html", error=str(e))


@app.route("/ask", methods=["POST"])
def ask():
    try:
        document_id = request.form.get("document_id", "")
        question = request.form.get("question", "")

        if not document_id or not question:
            return render_template("index.html", error="Document ID and question are required")

        document_text = document_store.get(document_id)

        if not document_text:
            return render_template("index.html", error="Document not found")

        if AI_PROVIDER == "ollama":
            result = OllamaService.ask(question, document_text)
        elif AI_PROVIDER == "gemini":
            # assume GeminiService exposes a sync ask method
            result = GeminiService.ask_sync(question, document_text)
        else:
            # default to OpenAI sync method
            result = OpenAIService.ask_sync(question, document_text)

        answer = result.get("answer") if isinstance(result, dict) else str(result)
        confidence = result.get("confidence") if isinstance(result, dict) else None

        return render_template(
            "result.html",
            answer=answer,
            confidence=confidence
        )

    except Exception as e:
        logger.exception("Ask failed")
        return render_template("index.html", error="AI processing failed: " + str(e))


# Preserve original commented FastAPI code for reference
# @app.post("/upload")
# async def upload(file: UploadFile = File(...)):
#     try:
#         document_id = await DocumentService.process_file(file)
#         return {"document_id": document_id}
#     except Exception as e:
#         logger.error(str(e))
#         raise HTTPException(status_code=400, detail=str(e))
#
#
# @app.post("/ask")
# async def ask_question(request: QuestionRequest, ai_provider=None):
#     document_text = document_store.get(request.document_id)
#
#     if not document_text:
#         raise HTTPException(status_code=404, detail="Document not found")
#
#     try:
#         if ai_provider == "ollama":
#             result = OllamaService.ask(request.question, document_text)
#         elif ai_provider == "gemini":
#                     result = GeminiService.GeminiService.ask_sync(request.question, document_text)
#         else:
#             result = await OpenAIService.ask(
#                 request.question,
#                 document_text
#             )
#
#         return result
#
#     except Exception as e:
#         logger.error(str(e))
#         raise HTTPException(status_code=500, detail="AI processing failed")
#
# if __name__ == "__main__":
#     import uvicorn
#     # Run the ASGI app directly so `python app.py` starts the server.
#     uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)