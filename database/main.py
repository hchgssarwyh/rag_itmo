from fastapi import FastAPI, UploadFile, File, HTTPException
from utils import process_document, add_document_to_db, search_in_db
import os
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
'''TODO:
    1. Добавить ручку на загрузку нескольких файлов (сейчас только одного)
    3. Не предусмотрена работа с чанками, нужно разбивать документ + добавить вытаскивание таблиц из пдф
        (таблицы сделал но проверить)
    '''
load_dotenv()

app = FastAPI()

COLLECTION_NAME = os.getenv("COLLECTION_NAME")
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = os.getenv("CHROMA_PORT")  # Исправлена опечатка

client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=int(CHROMA_PORT),  # Исправлена опечатка
    settings=Settings()
)

# Используйте SentenceTransformerEmbeddingFunction для указания вашей модели
model_name = "all-MiniLM-L6-v2"
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=sentence_transformer_ef,
)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        document_text = process_document(file.filename, content)
        add_document_to_db(document_text, collection)
        return {"filename": file.filename, "status": "Uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search_document(query: str):
    try:
        results = search_in_db(query, collection)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
