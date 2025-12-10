# Insurance Document Parsers

This directory contains documentation for each supported document parser.

## Overview

The Insurance Policy Parser API uses a modular parser architecture where each insurance provider/document type has its own dedicated parser class. This allows for:

- **Maintainability**: Each parser is isolated and can be updated independently
- **Extensibility**: New parsers can be added without modifying existing code
- **Testability**: Each parser can be tested in isolation

## Directory Structure

```
parsers/
├── __init__.py           # Package exports
├── base_parser.py        # Abstract base class
├── discovery_parser.py   # Discovery Insure parser
├── santam_parser.py      # Santam parser (stub)
└── generic_parser.py     # Fallback parser

docs/parsers/
├── README.md             # This file
├── discovery_insure.md   # Discovery parser documentation
├── santam.md             # Santam parser documentation
└── adding_new_parser.md  # Guide for adding new parsers
```

## Supported Document Types

| Insurer | Document Type | GUID | Status |
|---------|--------------|------|--------|
| Discovery Insure | Policy Schedule | `d1s0-p0l1-sch3-v001` | ✅ Active |
| Discovery Insure | Quote Schedule | `d1s0-qu0t-sch3-v001` | ✅ Active |
| Santam | Policy Schedule | `s4nt-p0l1-sch3-v001` | 🔸 Stub |
| Old Mutual | Policy Schedule | `0ldm-p0l1-sch3-v001` | 🔸 Stub |
| OUTsurance | Policy Schedule | `0uts-p0l1-sch3-v001` | 🔸 Stub |

## How It Works

### 1. Document Identification

When a PDF is uploaded with `auto-detect`, the system:

1. Extracts text from all pages
2. Tries each parser's `identify_document()` method
3. Uses the first parser that returns `True`
4. Falls back to `GenericParser` if none match

### 2. Parsing

Once a parser is selected:

1. `extract_text()` populates `pages_text` and `pages_tables`
2. `parse()` extracts structured data using regex patterns
3. Results are returned as a JSON dictionary

### 3. Document GUIDs

Each document type has a unique GUID for explicit parser selection:

```python
class DocumentGuid(str, Enum):
    DISCOVERY_POLICY_SCHEDULE_V1 = "d1s0-p0l1-sch3-v001"
    AUTO_DETECT = "auto-d3t3-ct00-0000"
```

## Parser Documentation

- [Discovery Insure](./discovery_insure.md) - Full documentation
- [Santam](./santam.md) - Stub implementation
- [Adding New Parsers](./adding_new_parser.md) - Development guide

## Quick Reference

### API Endpoints

```bash
# Get all document types
GET /document-types

# Get specific document type info
GET /document-type/{guid}

# Parse with auto-detect
POST /parse-from-url
{
  "pdf_url": "https://...",
  "document_guid": "auto-d3t3-ct00-0000"
}

# Parse with specific parser
POST /parse-from-url
{
  "pdf_url": "https://...",
  "document_guid": "d1s0-p0l1-sch3-v001"
}
```

### Creating a New Parser

1. Create `parsers/new_insurer_parser.py`
2. Inherit from `BaseParser`
3. Implement `identify_document()` and `parse()`
4. Add to `document_types.py`
5. Export from `parsers/__init__.py`
6. Create documentation in `docs/parsers/`

See [Adding New Parsers](./adding_new_parser.md) for detailed instructions.

