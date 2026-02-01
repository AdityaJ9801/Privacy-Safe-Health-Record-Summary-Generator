"""Request schemas for API endpoints."""

from typing import Optional

from pydantic import BaseModel, Field


class TextSummaryRequest(BaseModel):
    """Request schema for text summarization."""
    
    text: str = Field(..., description="Medical report text to summarize")
    max_length: Optional[int] = Field(
        None,
        description="Maximum length of summary",
        ge=50,
        le=2048,
    )
    temperature: float = Field(
        default=0.7,
        description="Sampling temperature for generation",
        ge=0.1,
        le=1.0,
    )


class QuestionAnswerRequest(BaseModel):
    """Request schema for question answering."""
    
    text: str = Field(..., description="Medical report text")
    question: str = Field(..., description="Question to answer")


class RAGSummaryRequest(BaseModel):
    """Request schema for RAG-based summarization."""
    
    query: str = Field(
        default="Provide a comprehensive summary of the medical report",
        description="Query for retrieval",
    )
    top_k: Optional[int] = Field(
        None,
        description="Number of chunks to retrieve",
        ge=1,
        le=20,
    )


class RAGQuestionRequest(BaseModel):
    """Request schema for RAG-based question answering."""
    
    question: str = Field(..., description="Question to answer")
    top_k: Optional[int] = Field(
        None,
        description="Number of chunks to retrieve",
        ge=1,
        le=20,
    )

