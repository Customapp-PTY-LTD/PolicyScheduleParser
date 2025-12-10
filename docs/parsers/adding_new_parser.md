# Adding a New Document Parser

This guide explains how to add support for a new insurance document type.

## Prerequisites

- Sample PDF documents from the insurer
- Understanding of regex patterns
- Familiarity with Python classes

## Step 1: Create the Parser File

Create a new file in `parsers/` directory:

```python
# parsers/new_insurer_parser.py

"""
New Insurer Policy Schedule Parser
Extracts data from New Insurer policy schedule PDFs
"""

import re
from typing import Dict
from .base_parser import BaseParser


class NewInsurerParser(BaseParser):
    """
    Parser for New Insurer policy schedules.
    """
    
    @classmethod
    def get_document_name(cls) -> str:
        return "New Insurer Policy Schedule"
    
    @classmethod
    def get_supported_fields(cls) -> list:
        return [
            "policyNumber",
            "policyholder",
            "vehicles",
            "buildings",
            # ... list all fields this parser extracts
        ]
    
    def identify_document(self) -> bool:
        """Check if this is a New Insurer document"""
        all_text = " ".join(self.pages_text.values())
        # Use a unique identifier from the document
        return "New Insurer Ltd" in all_text or "NEWINS" in all_text
    
    def parse(self) -> Dict:
        """Parse the policy schedule"""
        policy = {
            "insurer": "New Insurer",
            "policyNumber": None,
            "policyholder": {},
            "vehicles": [],
            "buildings": [],
            # ... initialize all fields
        }
        
        # Call extraction methods
        self._parse_policy_info(policy)
        self._parse_policyholder(policy)
        self._parse_vehicles(policy)
        self._parse_buildings(policy)
        
        return policy
    
    def _parse_policy_info(self, policy: Dict):
        """Extract policy information"""
        all_text = self._get_all_text()
        
        # Example: Extract policy number
        match = re.search(r'Policy (?:Number|No)[.:\s]+(\w+)', all_text, re.IGNORECASE)
        if match:
            policy["policyNumber"] = match.group(1)
    
    def _parse_policyholder(self, policy: Dict):
        """Extract policyholder details"""
        all_text = self._get_all_text()
        
        policyholder = {
            "name": None,
            "idNumber": None,
            "address": None,
            "contact": {}
        }
        
        # Add extraction logic here
        
        policy["policyholder"] = policyholder
    
    def _parse_vehicles(self, policy: Dict):
        """Extract vehicle information"""
        # Add extraction logic here
        pass
    
    def _parse_buildings(self, policy: Dict):
        """Extract building information"""
        # Add extraction logic here
        pass
```

## Step 2: Export from Package

Update `parsers/__init__.py`:

```python
from .base_parser import BaseParser
from .discovery_parser import DiscoveryParser
from .santam_parser import SantamParser
from .generic_parser import GenericParser
from .new_insurer_parser import NewInsurerParser  # Add this

__all__ = [
    'BaseParser',
    'DiscoveryParser',
    'SantamParser',
    'GenericParser',
    'NewInsurerParser',  # Add this
]
```

## Step 3: Register Document Type

Update `document_types.py`:

### Add GUID to Enum

```python
class DocumentGuid(str, Enum):
    # ... existing GUIDs
    
    # New Insurer Documents
    NEW_INSURER_POLICY_SCHEDULE_V1 = "n3w1-p0l1-sch3-v001"
```

### Add to Registry

```python
DOCUMENT_TYPE_REGISTRY: Dict[str, DocumentTypeInfo] = {
    # ... existing entries
    
    DocumentGuid.NEW_INSURER_POLICY_SCHEDULE_V1.value: DocumentTypeInfo(
        guid=DocumentGuid.NEW_INSURER_POLICY_SCHEDULE_V1.value,
        name="New Insurer Policy Schedule",
        insurer="New Insurer",
        description="New Insurer insurance policy schedule document",
        parser_class_name="NewInsurerParser",
        status="active"  # or "stub" if not fully implemented
    ),
}
```

### Update Parser Registry

```python
@classmethod
def _initialize(cls):
    if cls._initialized:
        return
    
    from parsers import DiscoveryParser, SantamParser, GenericParser, NewInsurerParser
    
    cls._parser_classes = {
        "DiscoveryParser": DiscoveryParser,
        "SantamParser": SantamParser,
        "GenericParser": GenericParser,
        "NewInsurerParser": NewInsurerParser,  # Add this
    }
    cls._initialized = True
```

## Step 4: Create Documentation

Create `docs/parsers/new_insurer.md`:

```markdown
# New Insurer Policy Schedule Parser

## Document Type Information

| Property | Value |
|----------|-------|
| **GUID** | `n3w1-p0l1-sch3-v001` |
| **Parser Class** | `NewInsurerParser` |
| **Status** | Active |
| **File Location** | `parsers/new_insurer_parser.py` |

## Overview

Description of what this parser handles...

## Extracted Fields

| Field | Type | Description |
|-------|------|-------------|
| `policyNumber` | string | Policy identifier |
| ... | ... | ... |

## Extraction Patterns

Document your regex patterns here...

## Known Limitations

List any limitations...
```

## Step 5: Test the Parser

### Unit Tests

Create test file `tests/test_new_insurer_parser.py`:

```python
import pytest
from parsers import NewInsurerParser

class TestNewInsurerParser:
    def test_identify_document(self, sample_pdf_path):
        parser = NewInsurerParser(sample_pdf_path)
        parser.extract_text()
        assert parser.identify_document() == True
    
    def test_parse_policy_number(self, sample_pdf_path):
        parser = NewInsurerParser(sample_pdf_path)
        parser.extract_text()
        result = parser.parse()
        assert result["policyNumber"] is not None
```

### Integration Test

```bash
# Test with auto-detect
curl -X POST "http://localhost:8000/parse-from-url" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_url": "https://example.com/new-insurer-policy.pdf",
    "document_guid": "auto-d3t3-ct00-0000"
  }'

# Test with specific GUID
curl -X POST "http://localhost:8000/parse-from-url" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_url": "https://example.com/new-insurer-policy.pdf",
    "document_guid": "n3w1-p0l1-sch3-v001"
  }'
```

## Best Practices

### 1. Use the Base Parser Methods

Leverage helper methods from `BaseParser`:
- `_get_all_text()` - Get concatenated text
- `_find_page_containing(*keywords)` - Find specific page
- `_clean_amount(amount_str)` - Parse currency amounts

### 2. Handle Multiple Formats

Documents may have variations. Handle them gracefully:

```python
patterns = [
    r'Policy Number:\s*(\w+)',
    r'Policy No[.:\s]+(\w+)',
    r'Ref:\s*(\w+)',
]
for pattern in patterns:
    match = re.search(pattern, all_text, re.IGNORECASE)
    if match:
        policy["policyNumber"] = match.group(1)
        break
```

### 3. Validate Extracted Data

```python
def _parse_amount(self, text: str) -> float:
    amount = self._clean_amount(text)
    if amount and amount > 0:
        return amount
    return None
```

### 4. Document Your Patterns

Add comments explaining regex patterns:

```python
# Pattern: "Sum Insured: R 1,234,567.89" or "Sum Insured R1234567.89"
match = re.search(r'Sum Insured[:\s]+R\s*([\d,\s]+\.?\d*)', all_text)
```

### 5. Handle Missing Data Gracefully

Return `None` for missing fields rather than raising exceptions:

```python
policy["optionalField"] = extracted_value if extracted_value else None
```

## Checklist

Before submitting your parser:

- [ ] Parser class inherits from `BaseParser`
- [ ] `identify_document()` method implemented
- [ ] `parse()` method returns complete dictionary
- [ ] Added to `parsers/__init__.py`
- [ ] GUID added to `DocumentGuid` enum
- [ ] Registered in `DOCUMENT_TYPE_REGISTRY`
- [ ] Added to `ParserRegistry._initialize()`
- [ ] Documentation created in `docs/parsers/`
- [ ] Tests written and passing
- [ ] Tested with sample documents

