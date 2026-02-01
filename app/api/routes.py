"""API route definitions."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app import __version__
from app.models.model_loader import model_loader
from app.processors.document_processor import DocumentProcessor
from app.processors.image_processor import ImageProcessor
from app.rag.rag_pipeline import rag_pipeline
from app.schemas.requests import (
    QuestionAnswerRequest,
    RAGQuestionRequest,
    RAGSummaryRequest,
    TextSummaryRequest,
)
from app.schemas.responses import (
    AnswerResponse,
    DocumentUploadResponse,
    ErrorResponse,
    HealthResponse,
    RAGAnswerResponse,
    SummaryResponse,
)
from app.utils.logger import app_logger

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        model_loaded=model_loader.is_loaded() if model_loader.is_available() else False,
        version=__version__,
        ml_available=model_loader.is_available(),
    )


@router.post("/summarize", response_model=SummaryResponse)
async def summarize_text(request: TextSummaryRequest):
    """Generate summary from medical report text."""
    try:
        app_logger.info("Received summarization request")

        # Check if ML dependencies are available
        if not model_loader.is_available():
            raise HTTPException(
                status_code=503,
                detail="ML dependencies not available. Please install: pip install torch transformers accelerate bitsandbytes"
            )

        # Ensure model is loaded
        if not model_loader.is_loaded():
            model_loader.load_model()

        # Generate summary
        summary = model_loader.generate_summary(
            text=request.text,
            max_length=request.max_length,
            temperature=request.temperature,
        )

        return SummaryResponse(
            summary=summary,
            input_length=len(request.text),
            summary_length=len(summary),
        )

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error in summarization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=AnswerResponse)
async def analyze_report(request: QuestionAnswerRequest):
    """Analyze medical report and answer specific question."""
    try:
        app_logger.info("Received analysis request")

        # Check if ML dependencies are available
        if not model_loader.is_available():
            raise HTTPException(
                status_code=503,
                detail="ML dependencies not available. Please install: pip install torch transformers accelerate bitsandbytes"
            )

        # Ensure model is loaded
        if not model_loader.is_loaded():
            model_loader.load_model()

        # Generate answer
        answer = model_loader.analyze_report(
            text=request.text,
            query=request.question,
        )

        return AnswerResponse(
            question=request.question,
            answer=answer,
        )

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error in analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/document", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process medical document (PDF, TXT)."""
    try:
        app_logger.info(f"Received document upload: {file.filename}")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Validate file size
            DocumentProcessor.validate_file_size(tmp_path)
            
            # Process document
            text = DocumentProcessor.process_document(tmp_path)
            
            # Index with RAG
            rag_pipeline.process_large_document(text)
            
            return DocumentUploadResponse(
                filename=file.filename,
                file_size=len(content),
                format=Path(file.filename).suffix.lstrip("."),
                processed=True,
                message="Document processed and indexed successfully",
            )
            
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)
        
    except Exception as e:
        app_logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/image", response_model=DocumentUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """Upload and process medical image."""
    try:
        app_logger.info(f"Received image upload: {file.filename}")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Process image and extract text
            text = ImageProcessor.extract_text_from_image(tmp_path)
            
            # Index with RAG if text extracted
            if text.strip():
                rag_pipeline.process_large_document(text)
                message = "Image processed and text indexed successfully"
            else:
                message = "Image processed but no text extracted"
            
            return DocumentUploadResponse(
                filename=file.filename,
                file_size=len(content),
                format=Path(file.filename).suffix.lstrip("."),
                processed=True,
                message=message,
            )
            
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)
        
    except Exception as e:
        app_logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/summarize", response_model=SummaryResponse)
async def rag_summarize(request: RAGSummaryRequest):
    """Generate summary using RAG for large documents."""
    try:
        app_logger.info("Received RAG summarization request")

        # Check if ML dependencies are available
        if not model_loader.is_available():
            raise HTTPException(
                status_code=503,
                detail="ML dependencies not available. Please install: pip install torch transformers accelerate bitsandbytes langchain langchain-community chromadb sentence-transformers"
            )

        # Ensure model is loaded
        if not model_loader.is_loaded():
            model_loader.load_model()

        # Generate summary with RAG
        summary = rag_pipeline.generate_summary_with_rag(
            query=request.query,
            top_k=request.top_k,
        )

        return SummaryResponse(
            summary=summary,
            input_length=0,  # Not applicable for RAG
            summary_length=len(summary),
        )

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error in RAG summarization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/question", response_model=RAGAnswerResponse)
async def rag_question(request: RAGQuestionRequest):
    """Answer question using RAG for large documents."""
    try:
        app_logger.info("Received RAG question request")

        # Check if ML dependencies are available
        if not model_loader.is_available():
            raise HTTPException(
                status_code=503,
                detail="ML dependencies not available. Please install: pip install torch transformers accelerate bitsandbytes langchain langchain-community chromadb sentence-transformers"
            )

        # Ensure model is loaded
        if not model_loader.is_loaded():
            model_loader.load_model()

        # Answer question with RAG
        result = rag_pipeline.answer_question_with_rag(
            question=request.question,
            top_k=request.top_k,
        )

        return RAGAnswerResponse(
            question=result["question"],
            answer=result["answer"],
            num_chunks_used=result["num_chunks_used"],
            relevant_chunks=result["relevant_chunks"],
        )

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error in RAG question answering: {e}")
        raise HTTPException(status_code=500, detail=str(e))

