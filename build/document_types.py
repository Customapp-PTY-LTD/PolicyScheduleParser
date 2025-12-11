"""
Document Types and Parser Registry
Defines document GUIDs and maps them to their respective parser classes
"""

from enum import Enum
from typing import Dict, Type, Optional
from dataclasses import dataclass


class DocumentGuid(str, Enum):
    """
    Document type GUIDs.
    
    These GUIDs uniquely identify each document type supported by the parser.
    In production, these would be pulled from the database, but for now
    they are defined as an enum for type safety and auto-complete support.
    
    Format: {INSURER}_{DOCUMENT_TYPE}_{VERSION}
    """
    
    # Discovery Insure Documents
    DISCOVERY_POLICY_SCHEDULE_V1 = "d1s0-p0l1-sch3-v001"
    DISCOVERY_QUOTE_SCHEDULE_V1 = "d1s0-qu0t-sch3-v001"
    
    # Santam Documents
    SANTAM_POLICY_SCHEDULE_V1 = "s4nt-p0l1-sch3-v001"
    
    # Old Mutual Documents
    OLD_MUTUAL_POLICY_SCHEDULE_V1 = "0ldm-p0l1-sch3-v001"
    
    # Outsurance Documents
    OUTSURANCE_POLICY_SCHEDULE_V1 = "0uts-p0l1-sch3-v001"
    
    # Hollard Documents
    HOLLARD_PRIVATE_PORTFOLIO_V1 = "h0ll-pr1v-p0rt-v001"
    
    # Auto-detect (system will try to identify the document)
    AUTO_DETECT = "auto-d3t3-ct00-0000"


@dataclass
class DocumentTypeInfo:
    """
    Information about a document type.
    
    Attributes:
        guid: Unique identifier for the document type
        name: Human-readable name
        insurer: Insurance company name
        description: Description of the document type
        parser_class_name: Name of the parser class to use
        status: Implementation status (active, stub, deprecated)
    """
    guid: str
    name: str
    insurer: str
    description: str
    parser_class_name: str
    status: str = "active"


# Document type registry - maps GUIDs to their metadata
DOCUMENT_TYPE_REGISTRY: Dict[str, DocumentTypeInfo] = {
    DocumentGuid.DISCOVERY_POLICY_SCHEDULE_V1.value: DocumentTypeInfo(
        guid=DocumentGuid.DISCOVERY_POLICY_SCHEDULE_V1.value,
        name="Discovery Insure Policy Schedule",
        insurer="Discovery Insure",
        description="Discovery Insure policy schedule document containing vehicle, building, and contents cover details",
        parser_class_name="DiscoveryParser",
        status="active"
    ),
    DocumentGuid.DISCOVERY_QUOTE_SCHEDULE_V1.value: DocumentTypeInfo(
        guid=DocumentGuid.DISCOVERY_QUOTE_SCHEDULE_V1.value,
        name="Discovery Insure Quote Schedule",
        insurer="Discovery Insure",
        description="Discovery Insure quote schedule document (pre-policy)",
        parser_class_name="DiscoveryParser",
        status="active"
    ),
    DocumentGuid.SANTAM_POLICY_SCHEDULE_V1.value: DocumentTypeInfo(
        guid=DocumentGuid.SANTAM_POLICY_SCHEDULE_V1.value,
        name="Santam Policy Schedule",
        insurer="Santam",
        description="Santam insurance policy schedule",
        parser_class_name="SantamParser",
        status="stub"
    ),
    DocumentGuid.OLD_MUTUAL_POLICY_SCHEDULE_V1.value: DocumentTypeInfo(
        guid=DocumentGuid.OLD_MUTUAL_POLICY_SCHEDULE_V1.value,
        name="Old Mutual Policy Schedule",
        insurer="Old Mutual",
        description="Old Mutual insurance policy schedule",
        parser_class_name="GenericParser",
        status="stub"
    ),
    DocumentGuid.OUTSURANCE_POLICY_SCHEDULE_V1.value: DocumentTypeInfo(
        guid=DocumentGuid.OUTSURANCE_POLICY_SCHEDULE_V1.value,
        name="OUTsurance Policy Schedule",
        insurer="OUTsurance",
        description="OUTsurance insurance policy schedule",
        parser_class_name="GenericParser",
        status="stub"
    ),
    DocumentGuid.HOLLARD_PRIVATE_PORTFOLIO_V1.value: DocumentTypeInfo(
        guid=DocumentGuid.HOLLARD_PRIVATE_PORTFOLIO_V1.value,
        name="Hollard Private Portfolio Policy Schedule",
        insurer="Hollard Insurance",
        description="Hollard Private Portfolio policy schedule containing motor, household contents, all risks, and personal liability cover",
        parser_class_name="HollardParser",
        status="active"
    ),
}


class ParserRegistry:
    """
    Registry for document parsers.
    
    This class manages the mapping between document GUIDs and parser classes.
    It also handles auto-detection of document types.
    """
    
    _parser_classes: Dict[str, Type] = {}
    _initialized: bool = False
    
    @classmethod
    def _initialize(cls):
        """Lazy initialization of parser classes"""
        if cls._initialized:
            return
        
        # Import parser classes
        from parsers import DiscoveryParser, SantamParser, GenericParser, HollardParser
        
        cls._parser_classes = {
            "DiscoveryParser": DiscoveryParser,
            "SantamParser": SantamParser,
            "GenericParser": GenericParser,
            "HollardParser": HollardParser,
        }
        cls._initialized = True
    
    @classmethod
    def get_parser_class(cls, document_guid: str) -> Optional[Type]:
        """
        Get the parser class for a document GUID.
        
        Args:
            document_guid: The document type GUID
            
        Returns:
            Parser class or None if not found
        """
        cls._initialize()
        
        # Handle auto-detect
        if document_guid == DocumentGuid.AUTO_DETECT.value:
            return None  # Will be handled by auto-detection logic
        
        # Look up in registry
        doc_info = DOCUMENT_TYPE_REGISTRY.get(document_guid)
        if doc_info:
            return cls._parser_classes.get(doc_info.parser_class_name)
        
        return None
    
    @classmethod
    def get_parser_for_auto_detect(cls, pdf_path: str) -> Type:
        """
        Auto-detect document type and return appropriate parser.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Parser class that can handle the document
        """
        cls._initialize()
        
        from parsers import GenericParser
        
        # Create a temporary parser to extract text for identification
        temp_parser = GenericParser(pdf_path)
        temp_parser.extract_text()
        
        # Try each parser's identification method
        for parser_name, parser_class in cls._parser_classes.items():
            if parser_name == "GenericParser":
                continue  # Skip generic parser in auto-detect
            
            test_parser = parser_class(pdf_path)
            test_parser.pages_text = temp_parser.pages_text
            test_parser.pages_tables = temp_parser.pages_tables
            
            if test_parser.identify_document():
                return parser_class
        
        # Fallback to generic parser
        return GenericParser
    
    @classmethod
    def get_all_document_types(cls) -> list:
        """
        Get list of all registered document types.
        
        Returns:
            List of DocumentTypeInfo objects
        """
        return list(DOCUMENT_TYPE_REGISTRY.values())
    
    @classmethod
    def get_supported_document_types(cls) -> list:
        """
        Get list of document types that are fully supported (not stubs).
        
        Returns:
            List of DocumentTypeInfo objects for active parsers
        """
        return [
            doc_info for doc_info in DOCUMENT_TYPE_REGISTRY.values()
            if doc_info.status == "active"
        ]


def get_document_info(document_guid: str) -> Optional[DocumentTypeInfo]:
    """
    Get information about a document type by GUID.
    
    Args:
        document_guid: The document type GUID
        
    Returns:
        DocumentTypeInfo or None if not found
    """
    return DOCUMENT_TYPE_REGISTRY.get(document_guid)


def list_supported_insurers() -> list:
    """
    Get list of supported insurance companies.
    
    Returns:
        List of dictionaries with insurer information
    """
    insurers = {}
    for doc_info in DOCUMENT_TYPE_REGISTRY.values():
        if doc_info.insurer not in insurers:
            insurers[doc_info.insurer] = {
                "name": doc_info.insurer,
                "documents": [],
                "status": "stub"
            }
        
        insurers[doc_info.insurer]["documents"].append({
            "guid": doc_info.guid,
            "name": doc_info.name,
            "status": doc_info.status
        })
        
        # If any document is active, mark insurer as active
        if doc_info.status == "active":
            insurers[doc_info.insurer]["status"] = "active"
    
    return list(insurers.values())

