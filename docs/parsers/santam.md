# Santam Policy Schedule Parser

## Document Type Information

| Property | Value |
|----------|-------|
| **GUID** | `s4nt-p0l1-sch3-v001` |
| **Parser Class** | `SantamParser` |
| **Status** | 🔸 Stub (Not Implemented) |
| **File Location** | `parsers/santam_parser.py` |

## Overview

The Santam parser is currently a stub implementation. It identifies Santam documents but does not yet extract structured data.

## Document Identification

The parser identifies Santam documents by searching for "Santam" text in the document.

```python
def identify_document(self) -> bool:
    all_text = " ".join(self.pages_text.values())
    return "Santam" in all_text
```

## Current Output

When parsing a Santam document, the parser returns:

```json
{
  "insurer": "Santam",
  "status": "not_implemented",
  "message": "Santam parser is currently a stub. Full implementation pending.",
  "rawText": {
    "page1": "First 500 characters...",
    "page2": "First 500 characters...",
    "page3": "First 500 characters..."
  }
}
```

## Planned Fields

When fully implemented, this parser should extract:

| Field | Description |
|-------|-------------|
| `policyNumber` | Santam policy number |
| `policyholder` | Policyholder details |
| `vehicles` | Vehicle cover information |
| `buildings` | Building cover information |
| `contents` | Contents cover information |
| `liability` | Personal liability cover |

## Implementation Guide

To implement this parser:

### 1. Analyze Document Structure

First, obtain sample Santam policy schedule PDFs and analyze:
- Page layout and structure
- Key sections and their identifiers
- Data formats (dates, amounts, addresses)
- Table structures

### 2. Identify Key Patterns

Document common text patterns:
```python
# Example patterns to look for:
# - "Policy Number: XXXXX"
# - "Sum Insured: R XXX,XXX.XX"
# - "Monthly Premium: R XXX.XX"
```

### 3. Implement Extraction Methods

Follow the Discovery parser structure:
```python
def parse(self) -> Dict:
    policy = {
        "insurer": "Santam",
        "policyNumber": None,
        # ... other fields
    }
    
    self._parse_policy_info(policy)
    self._parse_policyholder(policy)
    # ... etc
    
    return policy

def _parse_policy_info(self, policy: Dict):
    all_text = self._get_all_text()
    
    match = re.search(r'Policy Number[:\s]+(\w+)', all_text)
    if match:
        policy["policyNumber"] = match.group(1)
```

### 4. Update Documentation

Once implemented, update this file with:
- All extracted fields
- Regex patterns used
- Known limitations
- Test examples

## Testing

To test with Santam documents:

```bash
curl -X POST "http://localhost:8000/parse-from-url" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_url": "https://example.com/santam-policy.pdf",
    "document_guid": "s4nt-p0l1-sch3-v001"
  }'
```

## Related Files

- Parser: `parsers/santam_parser.py`
- Base class: `parsers/base_parser.py`
- Document types: `document_types.py`

## Contributing

If you have access to Santam policy schedule samples and would like to implement this parser, please:

1. Fork the repository
2. Create a feature branch
3. Implement the extraction methods
4. Add comprehensive tests
5. Update this documentation
6. Submit a pull request

