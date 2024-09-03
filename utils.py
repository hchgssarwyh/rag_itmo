import requests
from sentence_transformers import SentenceTransformer
import io

# Загрузите модель SentenceTransformer
model = SentenceTransformer('sergeyzh/rubert-tiny-turbo')

def create_collection(collection_id, collection_name, metadata=None):
    url = "http://localhost:8000/api/v1/collections"
    if not metadata:
        metadata = {
            "description": "Default description",
            "created_by": "system"
        }
    payload = {
        "id": collection_id,
        "name": collection_name,
        "metadata": metadata
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200 and response.status_code != 409:  # 409 означает, что коллекция уже существует
        raise Exception(f"Failed to create collection in ChromaDB: {response.text}")

    return response.json()

def process_pdf(content):
    import pdfplumber
    text = ""
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:  # проверить, что текст не является None
                text += page_text + "\n"
    return text

def process_docx(content):
    import docx
    doc = docx.Document(io.BytesIO(content))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def process_txt(content):
    return content.decode("utf-8")

def process_document(filename, content):
    if filename.endswith(".pdf"):
        return process_pdf(content)
    elif filename.endswith(".docx"):
        return process_docx(content)
    elif filename.endswith(".txt"):
        return process_txt(content)
    else:
        raise ValueError("Unsupported document format")

def get_embedding(text):
    embeddings = model.encode([text])
    return embeddings[0].tolist()

def add_document_to_db(collection_id, document_data, embedding):
    url = f"http://localhost:8000/api/v1/collections/{collection_id}/add"
    payload = {
        "content": document_data,
        "embedding": embedding
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        print(f"Payload: {payload}")
        print(f"Headers: {response.headers}")
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        raise Exception(f"Failed to add document to ChromaDB: {response.text}")

    return True

def search_in_db(collection_id, query_text):
    query_embedding = get_embedding(query_text)
    url = f"http://localhost:8000/api/v1/collections/{collection_id}/query"
    payload = {"embedding": query_embedding}

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise Exception(f"Failed to search in ChromaDB: {response.text}")

    return response.json()['results']
