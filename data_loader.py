from openai import OpenAI
from llama_index.readers.file import PDFReader, ImageReader, DocxReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv
from pathlib import Path
import base64

load_dotenv()

client = OpenAI()
EMBED_MODEL = "text-embedding-3-large"
EMBED_DIM = 3072

splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)


def get_file_type(path: str) -> str:
    """Determine file type from extension"""
    ext = Path(path).suffix.lower()
    if ext == '.pdf':
        return 'pdf'
    elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp']:
        return 'image'
    elif ext in ['.docx', '.doc']:
        return 'word'
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def load_and_chunk_pdf(path: str):
    """Load and chunk PDF documents"""
    docs = PDFReader().load_data(file=path)
    texts = [d.text for d in docs if getattr(d, "text", None)]
    chunks = []
    for t in texts:
        if t and t.strip():
            chunks.extend(splitter.split_text(t))
    return chunks


def load_and_chunk_image(path: str):
    """Load and extract text from images using OCR"""
    try:
        # Try LlamaIndex ImageReader first
        docs = ImageReader().load_data(file=path)
        texts = [d.text for d in docs if getattr(d, "text", None)]
        
        # If no text extracted or empty, try OpenAI Vision API
        if not texts or not any(t.strip() for t in texts):
            print(f"Using Vision API for {path}")
            with open(path, 'rb') as img_file:
                img_data = img_file.read()
            
            # Use OpenAI Vision API for better extraction
            base64_image = base64.b64encode(img_data).decode('utf-8')
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": "Extract all text content from this image. If there are tables, preserve their structure. If there are diagrams or charts, describe them in detail."
                            },
                            {
                                "type": "image_url", 
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            texts = [response.choices[0].message.content]
        
        chunks = []
        for t in texts:
            if t and t.strip():
                chunks.extend(splitter.split_text(t))
        
        return chunks if chunks else [f"[Image file: {Path(path).name} - No text extracted]"]
        
    except Exception as e:
        print(f"Error processing image {path}: {e}")
        return [f"[Image file: {Path(path).name} - Processing error: {str(e)}]"]


def load_and_chunk_word(path: str):
    """Load and chunk Word documents"""
    try:
        docs = DocxReader().load_data(file=path)
        texts = [d.text for d in docs if getattr(d, "text", None)]
        chunks = []
        for t in texts:
            if t and t.strip():
                chunks.extend(splitter.split_text(t))
        return chunks if chunks else [f"[Empty Word document: {Path(path).name}]"]
    except Exception as e:
        print(f"Error processing Word document {path}: {e}")
        return [f"[Word document: {Path(path).name} - Processing error: {str(e)}]"]


def load_and_chunk_file(path: str):
    """Universal file loader that handles PDF, images, and Word docs"""
    file_type = get_file_type(path)
    
    if file_type == 'pdf':
        return load_and_chunk_pdf(path)
    elif file_type == 'image':
        return load_and_chunk_image(path)
    elif file_type == 'word':
        return load_and_chunk_word(path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for text chunks"""
    if not texts:
        return []
    
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]