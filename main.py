import logging
from fastapi import FastAPI
import inngest
import inngest.fast_api
from inngest.experimental import ai
from dotenv import load_dotenv
import uuid
import os
import datetime
from data_loader import load_and_chunk_file, embed_texts
from vector_db import QdrantStorage
from custom_types import RAGQueryResult, RAGSearchResult, RAGUpsertResult, RAGChunkAndSrc, OutputFormat

load_dotenv()

inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer()
)

@inngest_client.create_function(
    fn_id="RAG: Ingest File",
    trigger=inngest.TriggerEvent(event="rag/ingest_file"),
    throttle=inngest.Throttle(
        limit=2, 
        period=datetime.timedelta(minutes=1)
    ),
    rate_limit=inngest.RateLimit(
        limit=1,
        period=datetime.timedelta(hours=4),
        key="event.data.source_id",
    ),
)
async def rag_ingest_file(ctx: inngest.Context):
    """Ingest files of multiple formats: PDF, Word, Images"""
    def _load(ctx: inngest.Context) -> RAGChunkAndSrc:
        file_path = ctx.event.data["file_path"]
        source_id = ctx.event.data.get("source_id", file_path)
        chunks = load_and_chunk_file(file_path)
        return RAGChunkAndSrc(chunks=chunks, source_id=source_id)

    def _upsert(chunks_and_src: RAGChunkAndSrc) -> RAGUpsertResult:
        chunks = chunks_and_src.chunks
        source_id = chunks_and_src.source_id
        
        if not chunks:
            return RAGUpsertResult(ingested=0)
        
        vecs = embed_texts(chunks)
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads = [{"source": source_id, "text": chunks[i]} for i in range(len(chunks))]
        QdrantStorage().upsert(ids, vecs, payloads)
        return RAGUpsertResult(ingested=len(chunks))

    chunks_and_src = await ctx.step.run("load-and-chunk", lambda: _load(ctx), output_type=RAGChunkAndSrc)
    ingested = await ctx.step.run("embed-and-upsert", lambda: _upsert(chunks_and_src), output_type=RAGUpsertResult)
    return ingested.model_dump()


def get_system_prompt(output_format: str) -> str:
    """Generate system prompt based on output format"""
    prompts = {
        "short": "You answer questions concisely in 2-3 sentences using only the provided context.",
        "long": "You provide comprehensive, detailed answers using the provided context. Include all relevant information and explanations.",
        "bullet_points": "You answer questions using bullet points. Structure your response with clear, concise bullet points highlighting key information from the context.",
        "detailed": "You provide thorough, well-structured answers with multiple paragraphs. Include examples, explanations, and all relevant details from the context.",
        "tabular": "You answer questions in a structured, tabular format when appropriate. Use clear headings and organize information systematically. If the information fits a table structure, present it that way using markdown tables.",
        "summary": "You provide a summary-style answer that captures the main points from the context in a brief, organized manner."
    }
    return prompts.get(output_format, prompts["short"])


def get_user_instruction(output_format: str) -> str:
    """Generate user instruction based on output format"""
    instructions = {
        "short": "Answer concisely in 2-3 sentences.",
        "long": "Provide a comprehensive, detailed answer with all relevant information.",
        "bullet_points": "Structure your answer as clear bullet points.",
        "detailed": "Provide a thorough answer with multiple paragraphs, examples, and explanations.",
        "tabular": "If applicable, present the information in a markdown table or structured format with clear categories.",
        "summary": "Provide a well-organized summary of the main points."
    }
    return instructions.get(output_format, instructions["short"])


@inngest_client.create_function(
    fn_id="RAG: Query Documents",
    trigger=inngest.TriggerEvent(event="rag/query_documents_ai")
)
async def rag_query_documents_ai(ctx: inngest.Context):
    """Query documents with customizable output formats"""
    def _search(question: str, top_k: int = 5) -> RAGSearchResult:
        query_vec = embed_texts([question])[0]
        store = QdrantStorage()
        found = store.search(query_vec, top_k)
        return RAGSearchResult(contexts=found["contexts"], sources=found["sources"])

    question = ctx.event.data["question"]
    top_k = int(ctx.event.data.get("top_k", 5))
    output_format = ctx.event.data.get("output_format", "short")

    found = await ctx.step.run("embed-and-search", lambda: _search(question, top_k), output_type=RAGSearchResult)

    context_block = "\n\n".join(f"- {c}" for c in found.contexts)
    user_content = (
        "Use the following context to answer the question.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {question}\n\n"
        f"Instructions: {get_user_instruction(output_format)}"
    )

    adapter = ai.openai.Adapter(
        auth_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )

    res = await ctx.step.ai.infer(
        "llm-answer",
        adapter=adapter,
        body={
            "max_tokens": 2048,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": get_system_prompt(output_format)},
                {"role": "user", "content": user_content}
            ]
        }
    )

    answer = res["choices"][0]["message"]["content"].strip()
    return {"answer": answer, "sources": found.sources, "num_contexts": len(found.contexts)}


app = FastAPI()

inngest.fast_api.serve(app, inngest_client, [rag_ingest_file, rag_query_documents_ai])
