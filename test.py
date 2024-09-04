import chromadb
from chromadb.config import Settings
try:
    # Создание клиента
    chroma_client = chromadb.HttpClient(
    host='localhost',
    port='8000',
    settings=Settings()
)
    # Создание коллекции
    collection = chroma_client.get_or_create_collection(name="collection_name")
    print(collection)

except Exception as e:
    print(f"Произошла ошибка: {e}")
