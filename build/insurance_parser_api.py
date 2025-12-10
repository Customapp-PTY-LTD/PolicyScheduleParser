#!/usr/bin/env python3
"""
Insurance Policy Schedule Parser Web Service
Supports multiple insurance providers with a pluggable parser architecture
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
from typing import Optional
import logging
import base64
import requests
from pydantic import BaseModel
from urllib.parse import urlparse

from document_types import (
    DocumentGuid,
    ParserRegistry,
    get_document_info,
    list_supported_insurers,
    DOCUMENT_TYPE_REGISTRY
)
from parsers import GenericParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Insurance Policy Parser API",
    description="Extract structured data from insurance policy schedule PDFs",
    version="2.0.0"
)


# Request Models
class ParseUrlRequest(BaseModel):
    """Request model for parsing PDF from URL"""
    pdf_url: str
    document_guid: Optional[str] = DocumentGuid.AUTO_DETECT.value


class ParseJsonRequest(BaseModel):
    """Request model for parsing PDF from base64-encoded data"""
    filename: str
    document_guid: Optional[str] = DocumentGuid.AUTO_DETECT.value
    file_base64: str  # base64-encoded PDF bytes


# Helper Functions
def create_parser(pdf_path: str, document_guid: str):
    """
    Create appropriate parser for the document.
    
    Args:
        pdf_path: Path to the PDF file
        document_guid: Document type GUID or AUTO_DETECT
        
    Returns:
        Initialized parser instance with text extracted
    """
    if document_guid == DocumentGuid.AUTO_DETECT.value:
        # Auto-detect document type
        parser_class = ParserRegistry.get_parser_for_auto_detect(pdf_path)
        parser = parser_class(pdf_path)
        parser.extract_text()
    else:
        # Use specified parser
        parser_class = ParserRegistry.get_parser_class(document_guid)
        if not parser_class:
            # Fallback to generic if GUID not found
            logger.warning(f"Unknown document_guid: {document_guid}, using GenericParser")
            parser_class = GenericParser
        
        parser = parser_class(pdf_path)
        parser.extract_text()
    
    return parser


# API Endpoints

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "Insurance Policy Parser API",
        "version": "2.0.0"
    }


@app.get("/document-types")
async def get_document_types():
    """
    Get list of all supported document types.
    
    Returns information about each document type including:
    - GUID for API calls
    - Human-readable name
    - Associated insurer
    - Implementation status
    """
    document_types = []
    for guid, info in DOCUMENT_TYPE_REGISTRY.items():
        document_types.append({
            "guid": guid,
            "name": info.name,
            "insurer": info.insurer,
            "description": info.description,
            "status": info.status
        })
    
    return {
        "documentTypes": document_types,
        "autoDetectGuid": DocumentGuid.AUTO_DETECT.value,
        "totalCount": len(document_types)
    }


@app.get("/supported-insurers")
async def supported_insurers():
    """
    Get list of supported insurance providers.
    
    Groups document types by insurer and shows status for each.
    """
    insurers = list_supported_insurers()
    
    return {
        "insurers": insurers,
        "autoDetect": True,
        "autoDetectGuid": DocumentGuid.AUTO_DETECT.value
    }


@app.get("/document-type/{document_guid}")
async def get_document_type_info(document_guid: str):
    """
    Get detailed information about a specific document type.
    
    Args:
        document_guid: The document type GUID
        
    Returns:
        Detailed information about the document type
    """
    doc_info = get_document_info(document_guid)
    
    if not doc_info:
        raise HTTPException(
            status_code=404,
            detail=f"Document type not found: {document_guid}"
        )
    
    # Get parser class info
    parser_class = ParserRegistry.get_parser_class(document_guid)
    supported_fields = []
    if parser_class:
        supported_fields = parser_class.get_supported_fields()
    
    return {
        "guid": doc_info.guid,
        "name": doc_info.name,
        "insurer": doc_info.insurer,
        "description": doc_info.description,
        "status": doc_info.status,
        "parserClass": doc_info.parser_class_name,
        "supportedFields": supported_fields
    }


@app.post("/parse-from-url")
async def parse_from_url(payload: ParseUrlRequest):
    """
    Parse an insurance policy schedule from a public PDF URL.

    Body:
        {
          "pdf_url": "https://example.com/policy.pdf",
          "document_guid": "auto-d3t3-ct00-0000"  // Optional, defaults to auto-detect
        }
        
    Returns:
        Structured JSON data extracted from the policy
    """

    # Validate URL format
    parsed = urlparse(payload.pdf_url)
    if not parsed.scheme or not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid PDF URL")

    if not payload.pdf_url.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="URL must point to a PDF file")

    try:
        logger.info(f"Downloading PDF from URL: {payload.pdf_url}")

        # Download the file
        response = requests.get(payload.pdf_url, timeout=30)
        response.raise_for_status()

        pdf_bytes = response.content

        if not pdf_bytes or len(pdf_bytes) < 100:
            raise HTTPException(status_code=400, detail="Downloaded PDF is empty or too small")

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download PDF: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to download PDF: {str(e)}")

    # Save to temp file for parsing
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_path = tmp_file.name
        tmp_file.write(pdf_bytes)

    try:
        logger.info(
            f"Processing PDF from URL, size: {len(pdf_bytes)} bytes, "
            f"document_guid: {payload.document_guid}"
        )

        parser = create_parser(tmp_path, payload.document_guid)
        result = parser.parse()
        
        # Add metadata
        result["_metadata"] = {
            "documentGuid": payload.document_guid,
            "parserClass": parser.__class__.__name__,
            "sourceType": "url"
        }

        logger.info("Successfully parsed PDF from URL")

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error parsing PDF from URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/parse-json")
async def parse_policy_json(payload: ParseJsonRequest):
    """
    Parse an insurance policy schedule PDF from a JSON body.

    Body:
        {
          "filename": "policy.pdf",
          "document_guid": "auto-d3t3-ct00-0000",  // Optional, defaults to auto-detect
          "file_base64": "<base64-encoded PDF bytes>"
        }
        
    Returns:
        Structured JSON data extracted from the policy
    """

    # Decode base64
    try:
        pdf_bytes = base64.b64decode(payload.file_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="file_base64 must be valid base64-encoded data")

    # Optional: basic sanity check on size
    if not pdf_bytes or len(pdf_bytes) < 100:
        raise HTTPException(status_code=400, detail="Decoded PDF data looks too small or empty")

    # Write to temporary file (so we can reuse existing ParserFactory logic)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_path = tmp_file.name
        tmp_file.write(pdf_bytes)

    try:
        logger.info(
            f"Processing JSON-uploaded file: {payload.filename}, size: {len(pdf_bytes)} bytes, "
            f"document_guid: {payload.document_guid}"
        )

        parser = create_parser(tmp_path, payload.document_guid)
        result = parser.parse()
        
        # Add metadata
        result["_metadata"] = {
            "documentGuid": payload.document_guid,
            "parserClass": parser.__class__.__name__,
            "sourceType": "base64",
            "filename": payload.filename
        }

        logger.info(f"Successfully parsed JSON-uploaded file: {payload.filename}")

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error parsing JSON-uploaded file {payload.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/parse")
async def parse_policy(
    file: UploadFile = File(...),
    document_guid: Optional[str] = DocumentGuid.AUTO_DETECT.value
):
    """
    Parse an insurance policy schedule PDF (file upload).
    
    Args:
        file: PDF file to parse
        document_guid: Document type GUID (auto-detect by default)
    
    Returns:
        Structured JSON data extracted from the policy
    """
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_path = tmp_file.name
        content = await file.read()
        tmp_file.write(content)
    
    try:
        logger.info(f"Processing file: {file.filename}, size: {len(content)} bytes")
        
        parser = create_parser(tmp_path, document_guid)
        result = parser.parse()
        
        # Add metadata
        result["_metadata"] = {
            "documentGuid": document_guid,
            "parserClass": parser.__class__.__name__,
            "sourceType": "upload",
            "filename": file.filename
        }
        
        logger.info(f"Successfully parsed {file.filename}")
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error parsing {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")
        
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/parse-from-path")
async def parse_from_path(
    filepath: str,
    document_guid: Optional[str] = DocumentGuid.AUTO_DETECT.value
):
    """
    Parse an insurance policy schedule from a file path.
    
    Args:
        filepath: Absolute path to PDF file
        document_guid: Document type GUID (auto-detect by default)
    
    Returns:
        Structured JSON data extracted from the policy
    """
    
    # Validate file exists
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File not found: {filepath}")
    
    if not filepath.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        logger.info(f"Processing file from path: {filepath}")
        
        parser = create_parser(filepath, document_guid)
        result = parser.parse()
        
        # Add metadata
        result["_metadata"] = {
            "documentGuid": document_guid,
            "parserClass": parser.__class__.__name__,
            "sourceType": "filepath",
            "filepath": filepath
        }
        
        logger.info(f"Successfully parsed {filepath}")
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error parsing {filepath}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
