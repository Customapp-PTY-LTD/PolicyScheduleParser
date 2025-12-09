# Discovery Insure Policy Schedule Parser

## Overview
This project provides solutions to extract structured data from Discovery Insure policy schedule PDFs into a sensible JSON format. Two implementations are provided:

1. **C# using PdfPig** - For .NET applications
2. **Python using pdfplumber** - For Python applications (tested and working)

## Solution Comparison

### C# with PdfPig

**Advantages:**
- Strong typing with data models
- Better for enterprise .NET applications
- Integrates well with existing C# codebases
- Excellent performance

**Implementation:**
```csharp
using UglyToad.PdfPig;

var policy = DiscoveryInsurePolicyParser.ParsePolicyDocument(pdfPath);
string json = DiscoveryInsurePolicyParser.ToJson(policy);
```

**Setup:**
```bash
# Install PdfPig via NuGet
dotnet add package PdfPig
```

### Python with pdfplumber

**Advantages:**
- Simpler setup and usage
- Better text extraction with layout awareness
- Excellent table extraction capabilities
- Easy to test and modify

**Implementation:**
```python
from discovery_parser import DiscoveryInsureParser

parser = DiscoveryInsureParser(pdf_path)
policy_data = parser.parse()
```

**Setup:**
```bash
pip install pdfplumber
```

## JSON Output Structure

The parser produces a comprehensive JSON structure with the following sections:

```json
{
  "planNumber": "4000638715",
  "planType": "Classic",
  "quoteEffectiveDate": "19/04/2022",
  "commencementDate": "01/04/2015",
  "planholder": {
    "name": "Mr Cedric Percival Keown",
    "idNumber": "6908155180084",
    "dateOfBirth": "15/08/1969",
    "maritalStatus": "Married",
    "residentialAddress": { ... },
    "contact": {
      "email": "cedric.keown@gmail.com",
      "cellphone": "0833777500",
      "homePhone": "0219757852",
      "workPhone": "0861007339"
    }
  },
  "payment": {
    "paymentType": "Debit Order",
    "accountHolder": "Cedric Percival Keown",
    "bank": "First National Bank",
    "accountType": "Cheque",
    "branchCode": "250655",
    "debitDay": 1,
    "paymentFrequency": "Monthly"
  },
  "motorVehicles": [
    {
      "vehicleNumber": 1,
      "make": "VOLVO",
      "model": "XC40 T5 R-DESIGN AWD",
      "registration": "TBA",
      "primaryDriver": "Cedric Percival Keown",
      "premium": 1007.46,
      "excess": {
        "basic": 3500.00,
        "voluntary": 0.00,
        "total": 3500.00
      },
      "details": {
        "yearOfManufacture": 2020,
        "colour": "Silver",
        "vinNumber": "YVIXZ16ACL2284606",
        "trackingDevice": "Tracker",
        "financeHouse": "Wesbank"
      }
    }
  ],
  "buildings": [
    {
      "address": "13, Clarkia Street, Durbanville",
      "effectiveDate": "01/04/2015",
      "sumInsured": 3880016.42,
      "premium": 740.59,
      "coverType": "Comprehensive"
    }
  ],
  "householdContents": {
    "address": "13, Clarkia Street, Durbanville",
    "sumInsured": 495821.91,
    "premium": 526.40
  },
  "personalLiability": {
    "sumInsured": 5000000.00,
    "premium": 5.05
  },
  "currentMonthlyPremium": 4119.89,
  "additionalBenefits": {
    "sasria": 24.53,
    "vitalitydrive": 170.00
  }
}
```

## Key Features

### 1. Hierarchical Data Structure
The JSON output mirrors the document structure:
- Plan-level information (header)
- Planholder details
- Payment information
- Asset coverage (vehicles, buildings, contents)
- Liability coverage
- Financial summary

### 2. Data Types Preserved
- Dates: Extracted and kept as strings (can be converted to date objects)
- Currency: Converted to decimal/float values (ZAR)
- Numbers: ID numbers as strings, quantities as integers
- Text: Proper names, addresses, etc.

### 3. Relational Data
- Multiple motor vehicles handled as an array
- Multiple buildings handled as an array
- Driver details linked to vehicles
- Finance houses linked to assets

## Usage Examples

### Python Implementation

```python
#!/usr/bin/env python3
from discovery_parser import DiscoveryInsureParser
import json

# Parse the PDF
parser = DiscoveryInsureParser('policy_schedule.pdf')
policy = parser.parse()

# Access specific data
print(f"Planholder: {policy['planholder']['name']}")
print(f"Monthly Premium: R{policy['currentMonthlyPremium']}")

# List all vehicles
for vehicle in policy['motorVehicles']:
    print(f"  {vehicle['make']} {vehicle['model']} - R{vehicle['premium']}")

# Save to file
with open('output.json', 'w') as f:
    json.dump(policy, f, indent=2)
```

### C# Implementation

```csharp
using System;
using DiscoveryInsureParser;

class Program
{
    static void Main()
    {
        var policy = DiscoveryInsurePolicyParser.ParsePolicyDocument("policy.pdf");
        
        // Access data
        Console.WriteLine($"Planholder: {policy.Planholder.Name}");
        Console.WriteLine($"Monthly Premium: R{policy.CurrentMonthlyPremium}");
        
        // List vehicles
        foreach (var vehicle in policy.MotorVehicles)
        {
            Console.WriteLine($"  {vehicle.Make} {vehicle.Model} - R{vehicle.Premium}");
        }
        
        // Export to JSON
        string json = DiscoveryInsurePolicyParser.ToJson(policy);
        File.WriteAllText("output.json", json);
    }
}
```

## Advanced Parsing Techniques

### 1. Pattern Matching with Regex
Both implementations use regular expressions to extract specific data:

```python
# Extract plan number
match = re.search(r'Plan number\s+(\d+)', page_text)
if match:
    plan_number = match.group(1)
```

### 2. Multi-Page Section Handling
The parser intelligently scans multiple pages for repeated sections:

```python
# Motor vehicles can span pages 6-11
for page_num in range(6, 12):
    page_text = self.pages_text.get(page_num, "")
    if contains_vehicle_data(page_text):
        vehicles.append(extract_vehicle(page_text))
```

### 3. Table Extraction (Optional Enhancement)
For more complex tables, you can use pdfplumber's table extraction:

```python
with pdfplumber.open("policy.pdf") as pdf:
    page = pdf.pages[3]  # Summary page
    tables = page.extract_tables()
    for table in tables:
        # Process table data
        pass
```

## Customization

### Adding New Fields
To extract additional fields, add them to the data model and parsing function:

**Python:**
```python
def parse_planholder_details(self, policy: Dict):
    # Add new field
    match = re.search(r'New Field:\s+(.+)', page_text)
    if match:
        planholder["newField"] = match.group(1)
```

**C#:**
```csharp
public class PlanholderDetails
{
    // Add new property
    public string NewField { get; set; }
}

// In parser
var newFieldMatch = Regex.Match(pageText, @"New Field:\s+(.+)");
if (newFieldMatch.Success)
    planholder.NewField = newFieldMatch.Groups[1].Value;
```

### Handling Variations
If your PDF has slight variations, make the regex patterns more flexible:

```python
# More flexible matching
match = re.search(r'(?:Plan number|Policy number|Plan no)\s+(\d+)', page_text)
```

## Error Handling

### Python
```python
try:
    parser = DiscoveryInsureParser(pdf_path)
    policy = parser.parse()
except FileNotFoundError:
    print("PDF file not found")
except Exception as e:
    print(f"Error parsing PDF: {e}")
    import traceback
    traceback.print_exc()
```

### C#
```csharp
try
{
    var policy = DiscoveryInsurePolicyParser.ParsePolicyDocument(pdfPath);
}
catch (FileNotFoundException)
{
    Console.WriteLine("PDF file not found");
}
catch (Exception ex)
{
    Console.WriteLine($"Error: {ex.Message}");
}
```

## Performance Considerations

### Python
- **pdfplumber** loads entire PDF into memory
- For large batches, process files sequentially
- Text extraction is relatively fast (<1 second per document)

### C#
- **PdfPig** is memory-efficient
- Can handle large documents well
- Faster than Python for high-volume processing

## Testing

Both implementations have been tested with the sample Discovery Insure policy schedule. To verify:

```bash
# Python
python3 discovery_parser.py

# C#
dotnet run
```

## Troubleshooting

### Issue: Missing Data
**Cause:** PDF structure varies or text extraction issues
**Solution:** 
1. Inspect the raw text: `print(page.extract_text())`
2. Adjust regex patterns
3. Check page numbers

### Issue: Incorrect Parsing
**Cause:** Regex pattern too strict or too loose
**Solution:** 
1. Test regex patterns individually
2. Use regex testers like regex101.com
3. Add debug logging

### Issue: Performance Problems
**Cause:** Large PDFs or inefficient parsing
**Solution:**
1. Process only required pages
2. Cache extracted text
3. Use compiled regex patterns

## Next Steps

### Enhancements
1. **OCR Support:** Add pytesseract for scanned documents
2. **Table Extraction:** Use pdfplumber's table features for tabular data
3. **Validation:** Add schema validation for parsed data
4. **Batch Processing:** Process multiple PDFs in parallel
5. **API Integration:** Create REST API endpoints for parsing
6. **Database Storage:** Store parsed data in SQL/NoSQL database

### Integration Examples
```python
# FastAPI endpoint
from fastapi import FastAPI, UploadFile

app = FastAPI()

@app.post("/parse-policy")
async def parse_policy(file: UploadFile):
    parser = DiscoveryInsureParser(file.file)
    return parser.parse()
```

## References

- [PdfPig GitHub](https://github.com/UglyToad/PdfPig)
- [pdfplumber Documentation](https://github.com/jsvine/pdfplumber)
- [Regular Expressions Guide](https://docs.python.org/3/library/re.html)

## License

This code is provided as-is for educational purposes.
