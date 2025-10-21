import asyncio
from pathlib import Path
import time
import gradio as gr
import inngest
from dotenv import load_dotenv
import os
import requests
from typing import Tuple
import shutil

load_dotenv()


def get_inngest_client() -> inngest.Inngest:
    """Get Inngest client instance"""
    return inngest.Inngest(app_id="rag_app", is_production=False)


def save_uploaded_file(file) -> Path:
    """Save uploaded file to uploads directory"""
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Get filename from the file object
    file_path = Path(file.name)
    dest_path = uploads_dir / file_path.name
    
    # Copy file to uploads directory
    shutil.copy2(file.name, dest_path)
    
    return dest_path


async def send_rag_ingest_event(file_path: Path) -> str:
    """Send ingestion event to Inngest"""
    client = get_inngest_client()
    await client.send(
        inngest.Event(
            name="rag/ingest_file",
            data={
                "file_path": str(file_path.resolve()),
                "source_id": file_path.name,
            },
        )
    )
    return file_path.name


def _inngest_api_base() -> str:
    """Get Inngest API base URL"""
    return os.getenv("INNGEST_API_BASE", "http://127.0.0.1:8288/v1")


def fetch_runs(event_id: str) -> list[dict]:
    """Fetch runs for a given event ID"""
    url = f"{_inngest_api_base()}/events/{event_id}/runs"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])
    except Exception as e:
        print(f"Error fetching runs: {e}")
        return []


def wait_for_run_output(event_id: str, timeout_s: float = 120.0, poll_interval_s: float = 0.5) -> dict:
    """Wait for run output with polling"""
    start = time.time()
    last_status = None
    while True:
        runs = fetch_runs(event_id)
        if runs:
            run = runs[0]
            status = run.get("status")
            last_status = status or last_status
            if status in ("Completed", "Succeeded", "Success", "Finished"):
                return run.get("output") or {}
            if status in ("Failed", "Cancelled"):
                raise RuntimeError(f"Function run {status}")
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Timed out waiting for run output (last status: {last_status})")
        time.sleep(poll_interval_s)


def upload_file(file) -> str:
    """Handle file upload"""
    if file is None:
        return "⚠️ Please upload a file first."
    
    try:
        file_path = save_uploaded_file(file)
        event_id = asyncio.run(send_rag_ingest_event(file_path))
        
        # Wait a bit for processing
        time.sleep(1)
        
        file_size = file_path.stat().st_size / 1024  # KB
        return f"""✅ **Successfully uploaded and processing!**

**File Details:**
- Name: `{file_path.name}`
- Type: `{file_path.suffix}`
- Size: `{file_size:.2f} KB`

The document is being processed and will be ready for querying shortly. You can now switch to the **Query Documents** tab to ask questions!"""
    except Exception as e:
        return f"❌ **Error uploading file:** {str(e)}\n\nPlease make sure all services are running:\n1. FastAPI server\n2. Inngest dev server\n3. Qdrant database"


async def send_rag_query_event(question: str, top_k: int, output_format: str) -> str:
    """Send query event to Inngest"""
    client = get_inngest_client()
    result = await client.send(
        inngest.Event(
            name="rag/query_documents_ai",
            data={
                "question": question,
                "top_k": top_k,
                "output_format": output_format,
            },
        )
    )
    return result[0]


def query_documents(question: str, top_k: int, output_format: str) -> Tuple[str, str]:
    """Query documents and return answer with sources"""
    if not question.strip():
        return "⚠️ Please enter a question.", ""
    
    try:
        # Send query event
        event_id = asyncio.run(send_rag_query_event(question.strip(), int(top_k), output_format))
        
        # Wait for result
        output = wait_for_run_output(event_id, timeout_s=60.0)
        
        answer = output.get("answer", "No answer generated.")
        sources = output.get("sources", [])
        num_contexts = output.get("num_contexts", 0)
        
        # Format sources
        if sources:
            sources_text = f"### 📚 Sources\n\n**Found {len(sources)} document(s) with {num_contexts} relevant chunk(s):**\n\n"
            for i, source in enumerate(sources, 1):
                sources_text += f"{i}. `{source}`\n"
        else:
            sources_text = "### ⚠️ No sources found\n\nPlease upload documents first before querying."
        
        return f"### 💡 Answer\n\n{answer}", sources_text
        
    except TimeoutError:
        return "⏱️ **Request timed out.** The query is taking longer than expected. Please try again with fewer chunks or a simpler question.", ""
    except Exception as e:
        error_msg = f"❌ **Error:** {str(e)}\n\n"
        if "Connection" in str(e):
            error_msg += "**Troubleshooting:**\n1. Check if Inngest dev server is running\n2. Verify FastAPI server is running\n3. Ensure Qdrant is accessible"
        return error_msg, ""


# Create Gradio interface with custom theme
with gr.Blocks(
    title="📚 RAG Document Q&A System",
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate",
    ),
    css="""
    .gradio-container {
        max-width: 1400px !important;
    }
    .output-markdown {
        padding: 20px;
        border-radius: 8px;
        background: #f8f9fa;
    }
    """
) as demo:
    
    gr.Markdown(
        """
        # 📚 RAG Document Q&A System
        
        ### Upload documents and get AI-powered answers with multiple output formats!
        
        **Supported Formats:** PDF, DOCX, DOC, PNG, JPG, JPEG, BMP, GIF, WEBP
        
        **Output Formats:** Short, Long, Bullet Points, Detailed, Tabular, Summary
        """
    )
    
    with gr.Tabs():
        # Upload Tab
        with gr.Tab("📤 Upload Documents"):
            with gr.Row():
                gr.Markdown(
                    """
                    ### Upload Your Documents
                    
                    Upload PDF files, Word documents, or images containing text.
                    """
                )
            
            with gr.Row():
                with gr.Column(scale=1):
                    file_input = gr.File(
                        label="📁 Choose a file",
                        file_types=[".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"],
                        type="filepath"
                    )
                    
                    upload_btn = gr.Button("📤 Upload & Process", variant="primary", size="lg")
                
                with gr.Column(scale=2):
                    upload_output = gr.Markdown(
                        label="Upload Status",
                        value="Upload a file to get started...",
                        elem_classes=["output-markdown"]
                    )
            
            upload_btn.click(
                fn=upload_file,
                inputs=[file_input],
                outputs=[upload_output]
            )
        
        # Query Tab
        with gr.Tab("🔍 Query Documents"):
            with gr.Row():
                with gr.Column(scale=1):
                    question_input = gr.Textbox(
                        label="❓ Your Question",
                        placeholder="What would you like to know?",
                        lines=4
                    )
                    
                    top_k_slider = gr.Slider(
                        minimum=1,
                        maximum=20,
                        value=5,
                        step=1,
                        label="📊 Number of chunks",
                        info="More chunks = more context"
                    )
                    
                    output_format_radio = gr.Radio(
                        choices=[
                            ("Short", "short"),
                            ("Long", "long"),
                            ("Bullet Points", "bullet_points"),
                            ("Detailed", "detailed"),
                            ("Tabular", "tabular"),
                            ("Summary", "summary")
                        ],
                        value="short",
                        label="📝 Output Format"
                    )
                    
                    query_btn = gr.Button("🚀 Get Answer", variant="primary", size="lg")
            
            with gr.Row():
                with gr.Column():
                    answer_output = gr.Markdown(elem_classes=["output-markdown"])
                    sources_output = gr.Markdown(elem_classes=["output-markdown"])
            
            query_btn.click(
                fn=query_documents,
                inputs=[question_input, top_k_slider, output_format_radio],
                outputs=[answer_output, sources_output]
            )
        
        # Info Tab
        with gr.Tab("ℹ️ Help"):
            gr.Markdown(
                """
                ## How to Use
                
                1. **Upload**: Go to Upload tab and select a file
                2. **Query**: Go to Query tab and ask questions
                3. **Format**: Choose your preferred output format
                
                ## Supported Files
                - PDF, Word (.docx, .doc)
                - Images (.png, .jpg, .jpeg, .bmp, .gif, .webp)
                
                ## Output Formats
                - **Short**: 2-3 sentences
                - **Long**: Comprehensive answer
                - **Bullet Points**: Structured lists
                - **Detailed**: Multi-paragraph
                - **Tabular**: Tables and categories
                - **Summary**: Main points
                """
            )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )