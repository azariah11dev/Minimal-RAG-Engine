import os
from fastapi import APIRouter, HTTPException
from fastapi import File, UploadFile

from src.services.rag.document_handler import documentHandler

doc_uploader = APIRouter(prefix="/document_uploader", tags=["document_uploader"])

def doc_dir(file_name: str = None):
    base_dir = os.path.join(os.path.dirname(__file__), "..", "models", "files")

    # Ensure directory exists
    if not os.path.exists(base_dir):
        os.makedirs(base_dir, exist_ok=True)

    # If file_name provided, return full file path
    if file_name:
        file_path = os.path.join(base_dir, file_name)
        if os.path.exists(file_path):
            raise FileExistsError(f"File '{file_name}' already exists.")
        return file_path

    return base_dir


@doc_uploader.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        file_path = doc_dir(file.filename)

        contents = await file.read()

        with open(file_path, "wb") as f:
            f.write(contents)

        # Process with DocumentHandler
        handler = documentHandler(file_path=file_path, file_name=file.filename)
        handler.load_document()

        return {"message": "Document uploaded and processed successfully."}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
