"""
Santam Policy Schedule Parser
Extracts data from Santam insurance policy schedule PDFs
"""

from typing import Dict
from .base_parser import BaseParser


class SantamParser(BaseParser):
    """
    Parser for Santam policy schedules.
    
    Status: Stub implementation - to be fully implemented.
    
    This parser will handle extraction of:
    - Policy details
    - Policyholder information
    - Vehicle cover
    - Building cover
    - Contents cover
    - Personal liability
    """
    
    @classmethod
    def get_document_name(cls) -> str:
        return "Santam Policy Schedule"
    
    @classmethod
    def get_supported_fields(cls) -> list:
        return [
            "policyNumber",
            "policyholder",
            "vehicles",
            "buildings",
            "contents",
            "liability"
        ]
    
    def identify_document(self) -> bool:
        """Check if this is a Santam document"""
        all_text = " ".join(self.pages_text.values())
        return "Santam" in all_text
    
    def parse(self) -> Dict:
        """
        Parse Santam policy schedule.
        
        Returns:
            Dictionary with parsed policy data or error message
        """
        return {
            "insurer": "Santam",
            "status": "not_implemented",
            "message": "Santam parser is currently a stub. Full implementation pending.",
            "rawText": self._get_preview_text()
        }
    
    def _get_preview_text(self) -> Dict[str, str]:
        """Get preview text from first few pages for debugging"""
        preview = {}
        for i, text in list(self.pages_text.items())[:3]:
            preview[f"page{i}"] = text[:500] + "..." if len(text) > 500 else text
        return preview

