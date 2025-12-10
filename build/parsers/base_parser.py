"""
Base Parser Class
Abstract base class for all insurance document parsers
"""

import pdfplumber
from typing import Dict
from abc import ABC, abstractmethod


class BaseParser(ABC):
    """
    Base class for insurance policy parsers.
    
    All document-specific parsers should inherit from this class and implement
    the required abstract methods.
    
    Attributes:
        pdf_path: Path to the PDF file to parse
        pages_text: Dictionary mapping page numbers to extracted text
        pages_tables: Dictionary mapping page numbers to extracted tables
    """
    
    def __init__(self, pdf_path: str):
        """
        Initialize the parser with a PDF file path.
        
        Args:
            pdf_path: Path to the PDF file to parse
        """
        self.pdf_path = pdf_path
        self.pages_text: Dict[int, str] = {}
        self.pages_tables: Dict[int, list] = {}
        
    def extract_text(self):
        """
        Extract text and tables from all pages of the PDF.
        
        This method populates the pages_text and pages_tables dictionaries
        with content from each page of the PDF document.
        """
        with pdfplumber.open(self.pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                self.pages_text[i] = page.extract_text() or ""
                # Also extract tables for structured data
                tables = page.extract_tables()
                if tables:
                    self.pages_tables[i] = tables
    
    def _get_all_text(self) -> str:
        """
        Get all pages text concatenated into a single string.
        
        Returns:
            Concatenated text from all pages
        """
        return "\n".join(self.pages_text.values())
    
    def _find_page_containing(self, *keywords) -> str:
        """
        Find the page text containing all specified keywords.
        
        Args:
            *keywords: Variable number of keywords to search for
            
        Returns:
            Text of the first page containing all keywords, or empty string
        """
        for page_num, text in self.pages_text.items():
            if all(kw in text for kw in keywords):
                return text
        return ""
    
    def _clean_amount(self, amount_str: str) -> float:
        """
        Clean and convert an amount string to float.
        
        Handles various formats like "R 1,234.56", "1 234.56", etc.
        
        Args:
            amount_str: String representation of the amount
            
        Returns:
            Float value of the amount, or None if conversion fails
        """
        if not amount_str:
            return None
        cleaned = amount_str.replace(',', '').replace(' ', '').replace('R', '').strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    @abstractmethod
    def identify_document(self) -> bool:
        """
        Check if this parser can handle the document.
        
        Returns:
            True if this parser can handle the document, False otherwise
        """
        raise NotImplementedError
    
    @abstractmethod
    def parse(self) -> Dict:
        """
        Parse the document and return structured data.
        
        Returns:
            Dictionary containing extracted policy data
        """
        raise NotImplementedError
    
    @classmethod
    def get_document_name(cls) -> str:
        """
        Get the human-readable name of the document type this parser handles.
        
        Returns:
            Document type name
        """
        return "Unknown Document"
    
    @classmethod
    def get_supported_fields(cls) -> list:
        """
        Get list of fields this parser can extract.
        
        Returns:
            List of field names that can be extracted
        """
        return []

