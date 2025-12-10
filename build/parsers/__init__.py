"""
Insurance Policy Schedule Parsers Package
Provides document-specific parsers for extracting data from insurance policy PDFs
"""

from .base_parser import BaseParser
from .discovery_parser import DiscoveryParser
from .santam_parser import SantamParser
from .generic_parser import GenericParser

__all__ = [
    'BaseParser',
    'DiscoveryParser',
    'SantamParser', 
    'GenericParser',
]

