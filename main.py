from fastapi import FastAPI, UploadFile, File, HTTPException
from utils import process_document, get_embedding, add_document_to_db, search_in_db
import os
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings


'''TODO:
    1. Добавить ручку на загрузку нескольких файлов (сейчас только одного)
    2. Использовать эмбеддер из функционала Chroma (позволяет выбрать любой с hf)
    3. Не предусмотрена работа с чанками, нужно разбивать документ + добавить вытаскивание таблиц из пдф
      (библа которая щас используется так может вроде)
    4. Дописать и отдебажить ручку search (не факт что надо)
    '''
# Загружаем переменные окружения из .env файла
load_dotenv()

app = FastAPI()

# Глобальные переменные для клиента и коллекции
client = None
collection = None

# Читаем имя коллекции, хост и порт из переменных окружения
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = os.getenv("CHROMA_PORT")
client = chromadb.HttpClient(
            host=CHROMA_HOST, # Используем переменные окружения
            port=int(CHROMA_PORT), # Порт лучше преобразовать в int
            settings=Settings()
        )
        # Создание или получение коллекции
collection = client.get_or_create_collection(name=COLLECTION_NAME)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        document_text = process_document(file.filename, content)
        document_embedding = get_embedding(document_text)
        add_document_to_db(document_text, document_embedding, collection)
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
