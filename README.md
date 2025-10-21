# 📚 Advanced RAG Document Q&A System

A production-ready Retrieval-Augmented Generation (RAG) application that supports **PDF**, **Word**, and **Image** documents with multiple output formats. Built with FastAPI, Inngest, Qdrant, OpenAI, and Gradio.

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- 📄 **Multi-Format Support**: PDF, DOCX/DOC, and Images (PNG, JPG, JPEG, BMP, GIF, WEBP)
- 🎯 **Multiple Output Formats**: 
  - **Short** - Concise 2-3 sentence answers
  - **Long** - Comprehensive detailed responses
  - **Bullet Points** - Structured lists
  - **Detailed** - Multi-paragraph with examples
  - **Tabular** - Organized tables and categories
  - **Summary** - Main points overview
- 🖼️ **Image OCR**: Automatic text extraction from images using OpenAI Vision API
- 🔍 **Semantic Search**: Advanced vector-based search with Qdrant
- 🤖 **AI-Powered Answers**: GPT-4o-mini with contextual understanding
- ⚡ **Async Workflows**: Reliable background processing with Inngest
- 🎨 **Modern UI**: Beautiful Gradio interface with tabs and real-time feedback
- 🛡️ **Rate Limiting**: Built-in throttling and rate limiting
- 📊 **Monitoring**: Inngest dashboard for workflow observability

## 🏗️ Architecture
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Gradio    │────▶│   FastAPI    │────▶│   Qdrant    │
│     UI      │     │   + Inngest  │     │  Vector DB  │
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   OpenAI     │
                    │ Embeddings   │
                    │   + LLM      │
                    └──────────────┘
```

**Technology Stack:**
- **FastAPI**: High-performance REST API server
- **Inngest**: Workflow orchestration with observability
- **Qdrant**: High-performance vector database
- **OpenAI**: text-embedding-3-large (3072D) + GPT-4o-mini + Vision API
- **LlamaIndex**: Document processing and chunking
- **Gradio**: Modern, interactive web interface

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ Python 3.12 or higher
- ✅ Docker (for Qdrant)
- ✅ Node.js (for Inngest CLI)
- ✅ OpenAI API key with sufficient credits

## 🚀 Quick Start

### 1. Initialize Project
```bash
# Initialize uv project
uv init .
```

### 2. Install Dependencies
```bash
# Install all required packages in one command
uv add fastapi inngest llama-index-core llama-index-readers-file python-dotenv qdrant-client uvicorn openai gradio pillow requests python-docx
```

### 3. Environment Setup

Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
INNGEST_API_BASE=http://127.0.0.1:8288/v1
```

**Important:** Replace `your_openai_api_key_here` with your actual OpenAI API key.

### 4. Start Qdrant

Using Docker:
```bash
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant
```

Verify it's running:
```bash
curl http://localhost:6333/healthz
# Expected: "healthz check passed"
```

### 5. Run the Application

You need **3 terminal windows** running simultaneously:

#### Terminal 1: FastAPI Server
```bash
uv run uvicorn main:app --reload
```
Server runs on: `http://localhost:8000`

#### Terminal 2: Inngest Dev Server
```bash
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery
```
Inngest UI: `http://localhost:8288`

#### Terminal 3: Gradio Interface
```bash
uv run python gradio_app.py
```
Gradio UI: `http://localhost:7860`

### 6. Access the Application

Open your browser and navigate to: **http://localhost:7860**

## 📖 Usage Guide

### Uploading Documents

1. Click on the **"📤 Upload Documents"** tab
2. Click **"Choose a file"** and select your document
3. Click **"Upload & Process"**
4. Wait for the success confirmation message

### Querying Documents

1. Switch to the **"🔍 Query Documents"** tab
2. Enter your question in the text box
3. Adjust the number of chunks (1-20, default: 5)
4. Select your preferred output format
5. Click **"🚀 Get Answer"**
6. View the answer and check the sources

### Example Queries
```
Short format: "What is the main topic of this document?"
Long format: "Explain the methodology in detail"
Bullet Points: "List the key findings"
Detailed: "Provide a comprehensive analysis of the results"
Tabular: "Compare the different approaches mentioned"
Summary: "Summarize the entire document"
```

## 📁 Project Structure
```
.
├── main.py                 # FastAPI app with Inngest functions
├── gradio_app.py          # Gradio web interface
├── data_loader.py         # Multi-format document processing
├── vector_db.py           # Qdrant vector database operations
├── custom_types.py        # Pydantic models with output formats
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore rules
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── QUICKSTART.md         # 5-minute quick start guide
└── uploads/              # Uploaded files storage (auto-created)
```

## 🔧 Configuration

### Document Processing Settings

- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Embedding Model**: text-embedding-3-large
- **Embedding Dimensions**: 3072

### Supported File Formats

| Type | Extensions | Processing Method |
|------|-----------|-------------------|
| PDF | `.pdf` | LlamaIndex PDFReader |
| Word | `.docx`, `.doc` | LlamaIndex DocxReader |
| Images | `.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`, `.webp` | ImageReader + Vision API |

### AI Settings

- **LLM Model**: GPT-4o-mini
- **Max Tokens**: 2048
- **Temperature**: 0.2
- **Vision Model**: GPT-4o-mini (for image text extraction)

### Vector Database

- **Collection Name**: `docs`
- **Distance Metric**: Cosine similarity
- **Default URL**: `http://localhost:6333`
- **Timeout**: 30 seconds

### Rate Limits

- **Throttle**: 2 requests per minute (per function)
- **Rate Limit**: 1 request per 4 hours per source_id
- **Prevents**: API overuse and duplicate processing

## 📊 Output Formats Explained

| Format | Description | Best For | Example |
|--------|-------------|----------|---------|
| **Short** | 2-3 sentences | Quick answers | "What is X?" |
| **Long** | Comprehensive | Full explanations | "Explain the process" |
| **Bullet Points** | Structured lists | Key points | "List the benefits" |
| **Detailed** | Multi-paragraph | In-depth analysis | "Analyze the results" |
| **Tabular** | Tables/Categories | Comparisons | "Compare A vs B" |
| **Summary** | Main points | Overview | "Summarize the doc" |

## 🖼️ Image Processing

The system uses a two-tier approach for image text extraction:

1. **LlamaIndex ImageReader**: Fast, basic OCR
2. **OpenAI Vision API**: Advanced extraction with context understanding (fallback)

**Best Practices for Images:**
- Use high-resolution images (300 DPI or higher)
- Ensure text is clearly visible and high-contrast
- Avoid heavily compressed or blurry images
- For complex diagrams, Vision API provides better descriptions

## 🎯 API Endpoints

### Inngest Functions

#### 1. RAG: Ingest File
- **Event**: `rag/ingest_file`
- **Throttle**: 2 requests/minute
- **Rate Limit**: 1 request per 4 hours per source
- **Accepts**: PDF, DOCX, DOC, Images
- **Steps**:
  1. Load and chunk document
  2. Generate embeddings (3072D)
  3. Upsert to Qdrant vector database

#### 2. RAG: Query Documents
- **Event**: `rag/query_documents_ai`
- **Parameters**:
  - `question` (string): User's query
  - `top_k` (int): Number of chunks to retrieve (1-20)
  - `output_format` (string): Response format
- **Steps**:
  1. Embed query
  2. Search Qdrant for similar chunks
  3. Generate formatted answer with GPT-4o-mini

### FastAPI Endpoints

Access API documentation at: `http://localhost:8000/docs`

## 🛠️ Development

### Running Tests
```bash
# Run the system test
uv run python test_system.py
```

### Code Quality
```bash
# Type checking
uv run mypy .

# Code formatting
uv run black .
uv run isort .

# Linting
uv run flake8 .
```

### Development Mode

All services support hot-reload during development:
```bash
# FastAPI with auto-reload
uv run uvicorn main:app --reload

# Gradio with auto-reload (edit and save files)
uv run python gradio_app.py
```

## 🐛 Troubleshooting

### Common Issues

#### 1. "Connection refused" Error

**Problem**: Cannot connect to Qdrant or Inngest

**Solution**:
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Restart Qdrant if needed
docker restart qdrant

# Ensure FastAPI is running before starting Inngest
```

#### 2. "OpenAI API Error"

**Problem**: API key issues or rate limits

**Solution**:
- Verify API key in `.env` file
- Check credits at: https://platform.openai.com/usage
- Check rate limits at: https://platform.openai.com/account/limits

#### 3. "Module not found" Error

**Problem**: Missing dependencies

**Solution**:
```bash
# Reinstall all dependencies
uv add fastapi inngest llama-index-core llama-index-readers-file python-dotenv qdrant-client uvicorn openai gradio pillow requests python-docx
```

#### 4. Image Processing Fails

**Problem**: Cannot extract text from images

**Solution**:
- Ensure image quality is high
- Check OpenAI API has Vision API access
- Verify image format is supported
- Check terminal logs for detailed errors

#### 5. Port Already in Use

**Problem**: Port 8000, 7860, or 8288 is occupied

**Solution**:
```bash
# For FastAPI (change port)
uv run uvicorn main:app --port 8001

# For Gradio (edit gradio_app.py)
# Change: server_port=7860 to server_port=7861

# Kill process on port
# Linux/Mac:
lsof -ti:8000 | xargs kill -9
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### 6. Slow Processing

**Problem**: Queries or uploads take too long

**Solution**:
- Reduce number of chunks (use 3-5 instead of 10-20)
- Use shorter documents
- Check internet connection speed
- Verify Qdrant performance with `curl http://localhost:6333/metrics`

### Debug Mode

Enable detailed logging:
```python
# Add to main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Checking Service Status
```bash
# Check all services
curl http://localhost:8000/docs          # FastAPI
curl http://localhost:8288               # Inngest
curl http://localhost:6333/healthz       # Qdrant
curl http://localhost:7860               # Gradio
```

## 📦 Dependencies

### Core Packages
```
fastapi>=0.104.0          # Web framework
inngest>=0.3.0            # Workflow orchestration
llama-index-core>=0.10.0  # Document processing
llama-index-readers-file  # File readers
python-dotenv>=1.0.0      # Environment variables
qdrant-client>=1.7.0      # Vector database
uvicorn>=0.24.0           # ASGI server
openai>=1.3.0             # OpenAI API
gradio>=4.0.0             # Web UI
```

### Additional Requirements
```
pillow>=10.0.0            # Image processing
requests>=2.31.0          # HTTP client
python-docx>=1.1.0        # Word documents
pydantic>=2.0.0           # Data validation
```

## 🚀 Production Deployment

### 1. Update Inngest Configuration
```python
# main.py
inngest_client = inngest.Inngest(
    app_id="rag_app",
    is_production=True,
    event_key=os.getenv("INNGEST_EVENT_KEY"),
    signing_key=os.getenv("INNGEST_SIGNING_KEY")
)
```

### 2. Use Managed Qdrant

Sign up for Qdrant Cloud and update:
```python
# vector_db.py
from qdrant_client import QdrantClient

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)
```

### 3. Deploy FastAPI

**Using Docker:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Deployment Platforms:**
- Railway
- Render
- Fly.io
- AWS (ECS, Lambda)
- Google Cloud Run
- Azure Container Apps

### 4. Deploy Gradio

**Hugging Face Spaces:**

Create `spaces.yml`:
```yaml
title: RAG Document Q&A
emoji: 📚
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "4.0.0"
app_file: gradio_app.py
```

**Other Options:**
- Railway
- Render
- Cloud VMs (AWS EC2, GCP Compute Engine)

### 5. Environment Variables for Production
```env
# Production .env
OPENAI_API_KEY=sk-prod-xxxxx
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
INNGEST_EVENT_KEY=your-event-key
INNGEST_SIGNING_KEY=your-signing-key
INNGEST_API_BASE=https://inn.gs
```

## 🔐 Security Best Practices

1. **Never commit `.env`** files to version control
2. **Use secrets management** (AWS Secrets Manager, HashiCorp Vault)
3. **Implement authentication** for production deployments
4. **Add file size limits** (e.g., max 10MB per upload)
5. **Scan uploads** for malware
6. **Use HTTPS** in production
7. **Rate limit** API endpoints
8. **Validate all inputs** before processing
9. **Monitor API usage** and costs
10. **Regular security audits**

## 📈 Performance Optimization

### Embedding Caching
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def embed_cached(text: str):
    return embed_texts([text])[0]
```

### Batch Processing

Process multiple documents in parallel:
```python
import asyncio

async def process_batch(files):
    tasks = [process_file(f) for f in files]
    return await asyncio.gather(*tasks)
```

### Vector Search Tuning

Adjust Qdrant search parameters:
```python
results = self.client.search(
    collection_name=self.collection,
    query_vector=query_vector,
    limit=top_k,
    score_threshold=0.7,  # Minimum similarity
    with_payload=True
)
```

## 📊 Monitoring & Observability

### Inngest Dashboard

Access at `http://localhost:8288` to monitor:
- Function execution history
- Success/failure rates
- Execution duration
- Error logs
- Replay failed runs

### Metrics to Track

- **Upload success rate**
- **Query response time**
- **Embedding generation time**
- **Vector search latency**
- **API costs** (OpenAI usage)
- **Error rates** by file type
- **User engagement metrics**

### Logging
```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"Processing file: {file_path}")
logger.error(f"Failed to process: {error}")
```

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`uv run python test_system.py`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for public APIs
- Include tests for new features
- Update documentation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for embeddings, LLM, and Vision APIs
- **Qdrant** for the excellent vector database
- **Inngest** for workflow orchestration
- **LlamaIndex** for document processing tools
- **Gradio** for the amazing UI framework
- **FastAPI** for the modern web framework

## 📞 Support

- **Documentation**: This README and additional guides
- **Issues**: [GitHub Issues](https://github.com/yourusername/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/your-repo/discussions)
- **Email**: your-email@example.com

## 🔮 Roadmap

### Planned Features

- [ ] Support for Excel, CSV, and TXT files
- [ ] Multi-language document support
- [ ] Conversation history and context memory
- [ ] Document comparison features
- [ ] Export answers to PDF/Word
- [ ] Advanced filtering and metadata search
- [ ] User authentication and document sharing
- [ ] Real-time collaborative querying
- [ ] Mobile app support
- [ ] Voice input for questions
- [ ] Summary generation for entire document collections

## 📚 Additional Resources

- [Quick Start Guide](QUICKSTART.md) - Get up and running in 5 minutes
- [Complete Setup Guide](COMPLETE_SETUP.md) - Detailed installation instructions
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Inngest Documentation](https://www.inngest.com/docs)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [OpenAI Documentation](https://platform.openai.com/docs)
- [Gradio Documentation](https://www.gradio.app/docs)

---

**Built with ❤️ using FastAPI, Inngest, Qdrant, OpenAI, and Gradio**

**⭐ Star this repo if you find it useful!**
