import uuid
from fastapi import UploadFile
from PyPDF2 import PdfReader
from storage.document_store import document_store
from utils.logger import get_logger

logger = get_logger(__name__)



import uuid
from PyPDF2 import PdfReader
from storage.document_store import document_store
from io import BytesIO


class DocumentService:

    @staticmethod
    def process_file_sync(file):
        content = file.read()
        document_id = str(uuid.uuid4())

        if file.filename.endswith(".pdf"):
            pdf = PdfReader(BytesIO(content))
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        elif file.filename.endswith(".txt"):
            text = content.decode("utf-8")
        else:
            raise ValueError("Unsupported file type")

        document_store.save(document_id, text)
        return document_id

        
# class DocumentService:

#     @staticmethod
#     async def process_file(file: UploadFile) -> str:
#         content = await file.read()
#         document_id = str(uuid.uuid4())

#         if file.filename.endswith(".pdf"):
#             text = DocumentService._extract_pdf_text(content)
#         elif file.filename.endswith(".txt"):
#             text = content.decode("utf-8")
#         else:
#             raise ValueError("Unsupported file type")

#         document_store.save(document_id, text)
#         logger.info(f"Document stored with ID: {document_id}")

#         return document_id

#     @staticmethod
#     def _extract_pdf_text(content: bytes) -> str:
#         from io import BytesIO

#         pdf = PdfReader(BytesIO(content))
#         text = ""

#         for page in pdf.pages:
#             text += page.extract_text() or ""

#         return text