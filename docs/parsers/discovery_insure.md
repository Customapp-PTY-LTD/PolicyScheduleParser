# Discovery Insure Policy Schedule Parser

## Document Type Information

| Property | Value |
|----------|-------|
| **GUID** | `d1s0-p0l1-sch3-v001` |
| **Parser Class** | `DiscoveryParser` |
| **Status** | Active |
| **File Location** | `parsers/discovery_parser.py` |

## Overview

The Discovery Insure parser extracts comprehensive data from Discovery Insure policy schedule PDFs. These documents typically contain information about motor vehicle cover, building insurance, household contents, and personal liability.

## Document Identification

The parser identifies Discovery documents by searching for "Discovery Insure" text anywhere in the document.

```python
def identify_document(self) -> bool:
    all_text = " ".join(self.pages_text.values())
    return "Discovery Insure" in all_text
```

## Extracted Fields

### Plan Information

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `planNumber` | string | Unique plan identifier | "4000638715" |
| `planType` | string | Type of plan (Classic, Essential, etc.) | "Classic" |
| `quoteEffectiveDate` | string | Date quote is effective (DD/MM/YYYY) | "19/04/2022" |
| `commencementDate` | string | Policy start date (DD/MM/YYYY) | "01/04/2015" |
| `validityPeriod` | string | Quote validity period | "30 days from quote date" |

### Planholder Details

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Full name with title |
| `planholderType` | string | Natural Person / Legal Entity |
| `idNumber` | string | South African ID number |
| `dateOfBirth` | string | Date of birth (DD/MM/YYYY) |
| `maritalStatus` | string | Married/Single/Divorced |
| `maidenName` | string | Maiden name if applicable |
| `residentialAddress` | string | Physical address |
| `postalAddress` | string | Postal address |
| `contact.homePhone` | string | Home telephone number |
| `contact.workPhone` | string | Work telephone number |
| `contact.cellphone` | string | Mobile phone number |
| `contact.email` | string | Email address |
| `preferredCommunication` | string | Preferred contact method |
| `electronicMarketing` | string | Marketing opt-in status |

### Payment Details

| Field | Type | Description |
|-------|------|-------------|
| `paymentType` | string | "Debit Order" or "EFT" |
| `payerName` | string | Name of account holder |
| `payerIdNumber` | string | Payer's ID number |
| `payerGender` | string | Male/Female |
| `accountHolder` | string | Bank account holder name |
| `accountNumber` | string | Masked account number |
| `bank` | string | Financial institution name |
| `accountType` | string | Cheque/Savings |
| `branchNameAndCode` | string | Branch details |
| `debitDay` | integer | Day of month for debit |
| `paymentFrequency` | string | Monthly/Annually |

### Financial Adviser

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Adviser's full name |
| `code` | string | FSP adviser code |
| `commissionSplit` | string | Commission percentage |

### Motor Vehicles

Each vehicle is an object with:

| Field | Type | Description |
|-------|------|-------------|
| `make` | string | Vehicle manufacturer |
| `model` | string | Vehicle model |
| `registration` | string | Registration number or "TBA" |
| `primaryDriver` | string | Primary driver name |
| `coverType` | string | "Comprehensive (Motor)" |
| `effectiveDate` | string | Cover start date |
| `premium` | float | Monthly premium |
| `carHire` | boolean | Car hire included |
| `stolenVehicleRecovery` | boolean | SVR included |
| `svrPremium` | float | SVR premium if applicable |
| `yearOfManufacture` | integer | Vehicle year |
| `vinNumber` | string | VIN number |
| `engineNumber` | string | Engine number |
| `colour` | string | Vehicle colour |
| `excess` | object | Excess amounts |

### Buildings

Each building is an object with:

| Field | Type | Description |
|-------|------|-------------|
| `address` | string | Full property address |
| `coverType` | string | "Comprehensive (Building)" |
| `effectiveDate` | string | Cover start date |
| `sumInsured` | float | Building value |
| `premium` | float | Monthly premium |

### Household Contents

| Field | Type | Description |
|-------|------|-------------|
| `address` | string | Property address |
| `coverType` | string | "Comprehensive (Contents)" |
| `effectiveDate` | string | Cover start date |
| `sumInsured` | float | Contents value |
| `comprehensivePremium` | float | Contents premium |
| `accidentalDamage.included` | boolean | AD cover included |
| `accidentalDamage.premium` | float | AD premium |

### Personal Liability

| Field | Type | Description |
|-------|------|-------------|
| `sumInsured` | float | Liability cover amount |
| `premium` | float | Monthly premium |
| `effectiveDate` | string | Cover start date |

### VitalityDrive

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "Active" or "Inactive" |
| `premium` | float | Monthly VitalityDrive premium |
| `rewardType` | string | "Cash to Planholder", etc. |
| `members` | array | List of member names |

### Commission

| Field | Type | Description |
|-------|------|-------------|
| `maximumCommission` | float | Maximum commission amount |
| `vatIncluded` | boolean | Whether VAT is included |
| `rates.nonMotor` | string | Non-motor commission rate |
| `rates.motor` | string | Motor commission rate |
| `rates.nonMotorSasria` | string | Non-motor SASRIA rate |
| `rates.motorSasria` | string | Motor SASRIA rate |
| `rates.vitalitydrive` | string | VitalityDrive rate |

### Other Fields

| Field | Type | Description |
|-------|------|-------------|
| `sasria` | float | SASRIA premium |
| `benefitsIncludedAtNoCost` | array | Free benefits list |
| `currentMonthlyPremium` | float | Total monthly premium |

## Extraction Patterns

### Plan Number
```python
patterns = [
    r'Plan number\s+(\d+)',
    r'Plan number:\s*(\d+)',
    r'Quote Schedule\s+Plan number\s+(\d+)',
]
```

### Vehicle Information
```python
# Pattern to find vehicle entries
vehicle_patterns = [
    r'([A-Z][A-Z-]+),\s*([A-Z0-9\s/.-]+?),\s*([A-Z]{2,3}\d+)',
    r'([A-Z][A-Z-]+),\s*([A-Z0-9\s/.-]+?),\s*(TBA)',
]
```

### Address Patterns
```python
# South African address format
addr_patterns = [
    r'(\d+,\s*[A-Za-z\s]+(?:street|Street|road|Road)...(?:Western Cape|Gauteng|...))',
]
```

## Known Limitations

1. **Building Sum Insured**: Sometimes not extracted if format varies significantly
2. **Multiple Pages**: Some detailed vehicle information requires dedicated vehicle pages
3. **Address Parsing**: Unusual address formats may not be fully captured
4. **Tables**: Complex table structures may require manual verification

## Testing

Use the following GUID to specifically test Discovery documents:
```
document_guid: "d1s0-p0l1-sch3-v001"
```

Or use auto-detect:
```
document_guid: "auto-d3t3-ct00-0000"
```

## Example API Call

```bash
curl -X POST "http://localhost:8000/parse-from-url" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_url": "https://example.com/discovery-policy.pdf",
    "document_guid": "d1s0-p0l1-sch3-v001"
  }'
```

## Adding New Fields

To add extraction for a new field:

1. Add the field to the `parse()` method's initial policy dictionary
2. Create a new `_parse_*` method or add to an existing one
3. Use regex patterns consistent with existing patterns
4. Add the field to `get_supported_fields()` class method
5. Update this documentation

## Related Files

- Parser: `parsers/discovery_parser.py`
- Base class: `parsers/base_parser.py`
- Document types: `document_types.py`

