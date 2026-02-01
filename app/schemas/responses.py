"""Response schemas for API endpoints."""

from typing import List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    version: str = Field(..., description="API version")
    ml_available: bool = Field(default=True, description="Whether ML dependencies are available")


class SummaryResponse(BaseModel):
    """Summary generation response."""
    
    summary: str = Field(..., description="Generated summary")
    input_length: int = Field(..., description="Length of input text")
    summary_length: int = Field(..., description="Length of summary")


class AnswerResponse(BaseModel):
    """Question answering response."""
    
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Generated answer")


class RAGAnswerResponse(BaseModel):
    """RAG-based question answering response."""
    
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Generated answer")
    num_chunks_used: int = Field(..., description="Number of chunks retrieved")
    relevant_chunks: Optional[List[str]] = Field(
        None,
        description="Retrieved chunks (optional)",
    )


class DocumentUploadResponse(BaseModel):
    """Document upload response."""
    
    filename: str = Field(..., description="Uploaded filename")
    file_size: int = Field(..., description="File size in bytes")
    format: str = Field(..., description="File format")
    processed: bool = Field(..., description="Whether processing succeeded")
    message: str = Field(..., description="Processing message")


class ErrorResponse(BaseModel):
    """Error response."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional details")

