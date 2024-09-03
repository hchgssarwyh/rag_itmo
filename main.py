from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from utils import process_document, get_embedding, add_document_to_db, search_in_db, create_collection

app = FastAPI()

# Укажите ID и имя вашей коллекции
COLLECTION_ID = 0
COLLECTION_NAME = "test"

# Создание коллекции при запуске приложения
@app.on_event("startup")
async def startup_event():
    try:
        create_collection(COLLECTION_ID, COLLECTION_NAME)
        print(f"Collection {COLLECTION_NAME} created successfully.")
    except Exception as e:
        print(f"Error creating collection: {e}")

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    content = await file.read()
    document_text = process_document(file.filename, content)
    document_embedding = get_embedding(document_text)
    print('Document Text:', document_text)
    print('Embedding:', document_embedding)
    add_document_to_db(COLLECTION_ID, document_text, document_embedding)
    return {"filename": file.filename, "status": "Uploaded successfully"}


@app.post("/search")
async def search_document(request: str):
    results = search_in_db(COLLECTION_ID, request)
    return {"results": results}
