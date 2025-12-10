"""
Generic Fallback Parser
Used when no specific parser matches the document
"""

from typing import Dict
from .base_parser import BaseParser


class GenericParser(BaseParser):
    """
    Generic fallback parser for unknown document formats.
    
    This parser is used when:
    - No specific parser matches the document
    - The document type cannot be auto-detected
    - A new document type needs to be analyzed
    
    It returns raw text from the document to help identify the format
    and develop a specific parser.
    """
    
    @classmethod
    def get_document_name(cls) -> str:
        return "Unknown Document Type"
    
    @classmethod
    def get_supported_fields(cls) -> list:
        return ["rawText"]
    
    def identify_document(self) -> bool:
        """
        Generic parser always returns True as a fallback.
        
        It should be checked last after all specific parsers.
        """
        return True
    
    def parse(self) -> Dict:
        """
        Basic extraction when document type is not recognized.
        
        Returns:
            Dictionary with raw text from first few pages and
            a message indicating the document type was not recognized.
        """
        return {
            "insurer": "Unknown",
            "status": "unrecognized",
            "rawText": self._get_preview_text(),
            "pageCount": len(self.pages_text),
            "message": (
                "Document type not recognized. "
                "Returning raw text from first 3 pages. "
                "Please check if a parser exists for this document type."
            )
        }
    
    def _get_preview_text(self) -> Dict[str, str]:
        """
        Get preview text from first few pages.
        
        Returns:
            Dictionary mapping page numbers to text content (truncated)
        """
        preview = {}
        for i, text in list(self.pages_text.items())[:3]:
            if text:
                preview[f"page{i}"] = text[:500] + "..." if len(text) > 500 else text
            else:
                preview[f"page{i}"] = "(empty page)"
        return preview

