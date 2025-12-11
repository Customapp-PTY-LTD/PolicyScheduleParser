# Hollard Private Portfolio Parser

## Document GUID
`h0ll-pr1v-p0rt-v001`

## Parser Class
`HollardParser` (`parsers/hollard_parser.py`)

## Overview
This parser extracts data from Hollard Private Portfolio policy schedule PDFs. These documents are multi-page schedules that contain detailed information about various insurance coverages including motor vehicles, household contents, all risks, and personal liability.

## Document Structure

Hollard Private Portfolio documents typically follow this structure:

### Page 1: Policy Details
- Policyholder name, address, contact details
- Quote/policy number
- Insurer information
- Period of insurance
- Start date

### Page 2: Broker & Administrator Details
- Broker company information
- Insurer contact details
- Administrator (Rodel) information

### Page 3: Premium Schedule
- Table of all sections (BUILDINGS, HOUSEHOLD CONTENTS, ALL RISKS, etc.)
- SASRIA inclusion status
- Sum insured per section
- Monthly premiums
- Totals (premium, fees, SASRIA, VAT, grand total)

### Pages 4+: Section Details
Each included section has its own detailed pages:
- **Household Contents**: Risk address, property type, security, cover options
- **All Risks**: Itemized list of unspecified and specified items
- **Personal Liability**: Cover limits and extensions
- **Motor Vehicles**: One or more vehicles with full details

## Extracted Fields

### Policy Level
| Field | Type | Description |
|-------|------|-------------|
| `quoteNumber` | string | Policy/quote reference number (e.g., "HOL-AMB0489-DOMEV2-9104682") |
| `policyType` | string | "MONTHLY" or "ANNUAL" |
| `periodOfInsurance` | string | Coverage period description |
| `startDate` | string | Policy start date |

### Policyholder
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Full name with title |
| `address.physical` | string | Physical address |
| `contact.cell` | string | Cell phone number |
| `contact.email` | string | Email address |
| `dateOfBirth` | string | Date of birth |

### Broker
| Field | Type | Description |
|-------|------|-------------|
| `company` | string | Broker company name |
| `branch` | string | Branch name |
| `contact.tel` | string | Phone number |
| `contact.email` | string | Email address |
| `fspLicence` | string | FSP licence number |

### Premium Schedule
| Field | Type | Description |
|-------|------|-------------|
| `sections` | array | List of included cover sections |
| `totalPremium` | number | Total monthly premium |
| `totalFees` | number | Administration fees |
| `sasria` | number | SASRIA premium |
| `grandTotal` | number | Final total including VAT |
| `vatAmount` | number | VAT amount |
| `commissionAmount` | number | Broker commission |

### Household Contents
| Field | Type | Description |
|-------|------|-------------|
| `itemReference` | string | Reference code (e.g., "HOU0001") |
| `riskAddress` | string | Property address |
| `sumInsured` | number | Total contents value |
| `premium` | number | Monthly premium |
| `typeOfHome` | string | Property type |
| `coverOption` | string | Cover type (Full cover, etc.) |
| `basicExcess` | number | Excess amount |
| `additionalCover` | object | Power surge, accidental damage, etc. |

### All Risks
| Field | Type | Description |
|-------|------|-------------|
| `itemNumber` | string | Item reference |
| `category` | string | Item category |
| `description` | string | Item description |
| `sumInsured` | number | Item value |
| `premium` | number | Monthly premium |

### Personal Liability
| Field | Type | Description |
|-------|------|-------------|
| `sumInsured` | number | Liability limit (e.g., 10,000,000) |
| `premium` | number | Monthly premium |
| `businessLiability` | boolean | Whether business liability is included |

### Motor Vehicles (array)
| Field | Type | Description |
|-------|------|-------------|
| `itemReference` | string | Reference code (e.g., "MOT0002") |
| `make` | string | Vehicle manufacturer |
| `model` | string | Vehicle model |
| `yearOfManufacture` | number | Year |
| `registration` | string | Registration plate |
| `vinNumber` | string | VIN/Chassis number |
| `engineNumber` | string | Engine number |
| `baseRetailValue` | number | Base retail value |
| `finalSumInsured` | number | Sum insured amount |
| `finalSumInsuredWithAccessories` | number | Sum insured including extras |
| `premium` | number | Monthly premium |
| `coverDetails.coverOption` | string | Comprehensive/Third Party |
| `coverDetails.thirdPartyLiability` | number | Third party limit |
| `excess.basic` | number | Basic excess |
| `registeredOwner.name` | string | Owner name |
| `driver.name` | string | Primary driver name |
| `driver.dateOfBirth` | string | Driver DOB |
| `driver.licenseType` | string | License code |

## Regex Patterns Used

### Quote Number
```regex
Quote number.*?:\s*([A-Z0-9-]+)
```

### Vehicle Details
```regex
Make\s*:\s*([^\n]+)
Model\s*:\s*([^\n]+)
Year of manufacture\s*:\s*(\d{4})
Registration number\s*:\s*([A-Z0-9]+)
VIN/Chassis number\s*:\s*([A-Z0-9]+)
```

### Premium Amounts
```regex
Total Premium\s+R\s*([\d\s,.]+)\s+R\s*([\d\s,.]+)
TOTAL\s+R\s*[\d\s,.]+\s+R\s*([\d\s,.]+)
```

### Sum Insured
```regex
Final Sum Insured\s*:\s*([\d\s,]+)
Final Sum Insured Including.*?:\s*([\d\s,]+)
```

## Example Output

```json
{
  "insurer": "Hollard Insurance",
  "documentType": "Private Portfolio",
  "quoteNumber": "HOL-AMB0489-DOMEV2-9104682",
  "policyType": "MONTHLY",
  "startDate": "01/01/2026",
  "policyholder": {
    "name": "MR P OOSTHUIZEN",
    "address": {
      "physical": "44 Van Bergen Street, Brackenhurst, BRACKENHURST, ALBERTON, 1448"
    },
    "contact": {
      "cell": "0828788877",
      "email": "corporate@flg.co.za"
    },
    "dateOfBirth": "28/09/1983"
  },
  "premiumSchedule": {
    "totalPremium": 3236.75,
    "totalFees": 129.47,
    "sasria": 17.31,
    "grandTotal": 3481.53,
    "vatAmount": 454.11,
    "commissionAmount": 473.47
  },
  "householdContents": [{
    "itemReference": "HOU0001",
    "riskAddress": "44 VAN BERGEN STREET, BRACKENHURST, BRACKENHURST, ALBERTON, 1448",
    "sumInsured": 1871120,
    "premium": 623.70,
    "typeOfHome": "Private Home",
    "coverOption": "Full cover"
  }],
  "allRisks": [{
    "itemNumber": "ALL0001",
    "category": "Clothing/Personal Effects",
    "description": "Unspecified",
    "sumInsured": 11047,
    "premium": 50.68
  }],
  "personalLiability": {
    "sumInsured": 10000000,
    "premium": 15.13
  },
  "motorVehicles": [
    {
      "itemReference": "MOT0002",
      "make": "FORD",
      "model": "FIESTA 1.0 ECOBOOST TITANIUM 5DR (2013 - 2018)",
      "yearOfManufacture": 2017,
      "registration": "FW78CGGP",
      "finalSumInsured": 168800,
      "premium": 422.25
    },
    {
      "itemReference": "MOT0003",
      "make": "SUZUKI",
      "model": "JIMNY 1.3 (2008 - 11/2018)",
      "yearOfManufacture": 2012,
      "registration": "BR45WTGP",
      "finalSumInsured": 133500,
      "premium": 276.26
    }
  ]
}
```

## Identification Method

The parser identifies Hollard documents by checking for:
- "HOLLARD" text in the document
- "PRIVATE PORTFOLIO" or "HOLLARD INSURANCE" text

```python
def identify_document(self) -> bool:
    all_text = " ".join(self.pages_text.values())
    return "HOLLARD" in all_text.upper() and \
           ("PRIVATE PORTFOLIO" in all_text.upper() or "HOLLARD INSURANCE" in all_text.upper())
```

## Known Limitations

1. **Driver Details Across Pages**: Driver information may span multiple pages, requiring page-by-page parsing
2. **Multiple Vehicles**: Each vehicle section starts on a new page, and driver details appear on the following page
3. **Additional Cover Options**: Not all optional covers are extracted (car hire, tyre cover, etc.)
4. **Specified All Risks**: Only unspecified all risks items are extracted

## Testing

Test the parser with:

```python
from parsers import HollardParser

parser = HollardParser("path/to/hollard_policy.pdf")
parser.extract_text()
parser.extract_tables()
result = parser.parse()

# Verify key fields
assert result["quoteNumber"] is not None
assert len(result["motorVehicles"]) > 0
```

## API Usage

```bash
# With specific GUID
curl -X POST "http://localhost:8000/parse-from-url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/hollard-policy.pdf",
    "document_guid": "h0ll-pr1v-p0rt-v001"
  }'

# With auto-detect
curl -X POST "http://localhost:8000/parse-from-url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/hollard-policy.pdf",
    "document_guid": "auto-d3t3-ct00-0000"
  }'
```

