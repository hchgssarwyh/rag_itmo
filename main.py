from fastapi import FastAPI, UploadFile, File, HTTPException
from utils import process_document, get_embedding, add_document_to_db, search_in_db, initialize_chroma
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

app = FastAPI()

# Читаем имя коллекции из переменных окружения
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

@app.on_event("startup")
async def startup_event():
    try:
        initialize_chroma(COLLECTION_NAME)
        print(f"Collection {COLLECTION_NAME} initialized successfully.")
    except Exception as e:
        print(f"Error initializing collection: {e}")

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        document_text = process_document(file.filename, content)
        document_embedding = get_embedding(document_text)
        add_document_to_db(document_text, document_embedding)
        return {"filename": file.filename, "status": "Uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_document(query: str):
    try:
        results = search_in_db(query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
