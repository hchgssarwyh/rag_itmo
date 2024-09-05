import io
import pdfplumber
import docx

def chunk_text(text, chunk_size=1000):
    """
    Разбивает текст на чанки фиксированного размера.
    """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def process_pdf(content):
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        text += " | ".join(str(cell) for cell in row) + "\n"
    except Exception as e:
        raise ValueError(f"Error processing PDF: {e}")

    return text

def process_docx(content):
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

def add_document_to_db(document_data, collection):
    document_chunks = chunk_text(document_data)
    for i, chunk in enumerate(document_chunks):
        chunk_id = f"{collection.name}-{i+1}"
        collection.add(
            documents=[chunk],
            metadatas=[{"source": "upload", "chunk_id": chunk_id}],
            ids=[chunk_id]
        )

def search_in_db(query_text, collection, num):
    try:
        results = collection.query(query_texts=[query_text], n_results=num)
        return results
    except Exception as e:
        raise e
