from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import io

# Загрузите модель SentenceTransformer
model = SentenceTransformer('sergeyzh/rubert-tiny-turbo')

client = None
collection = None

def initialize_chroma(collection_name):
    global client, collection
    client = chromadb.Client(settings=Settings())
    try:
        # Попытка получить коллекцию
        collection = client.get_collection(collection_name)
    except:
        # Коллекция не существует, нужно ее создать
        collection = client.create_collection(
            name=collection_name,
            metadata={"description": "Default description", "created_by": "system"}
        )

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

def add_document_to_db(document_data, embedding):
    collection.add(
        embeddings=[embedding],
        documents=[document_data],
        metadatas=[{"source": "upload"}]
    )

def search_in_db(query_text):
    query_embedding = get_embedding(query_text)
    results = collection.query(query_embedding, num_results=1)
    return results['results']
