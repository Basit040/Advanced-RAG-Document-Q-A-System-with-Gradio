import pydantic
from typing import Literal


class RAGChunkAndSrc(pydantic.BaseModel):
    chunks: list[str]
    source_id: str = None


class RAGUpsertResult(pydantic.BaseModel):
    ingested: int


class RAGSearchResult(pydantic.BaseModel):
    contexts: list[str]
    sources: list[str]


class RAGQueryResult(pydantic.BaseModel):
    answer: str
    sources: list[str]
    num_contexts: int


# Output format types
OutputFormat = Literal["short", "long", "bullet_points", "detailed", "tabular", "summary"]


class RAGQueryRequest(pydantic.BaseModel):
    question: str
    top_k: int = 5
    output_format: OutputFormat = "short"