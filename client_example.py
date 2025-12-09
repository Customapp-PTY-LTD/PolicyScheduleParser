#!/usr/bin/env python3
"""
Client examples for Insurance Policy Parser API
"""

import requests
import json
from pathlib import Path


class InsurancePolicyParserClient:
    """Client for interacting with the Insurance Policy Parser API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self):
        """Check if API is online"""
        response = requests.get(f"{self.base_url}/")
        return response.json()
    
    def get_supported_insurers(self):
        """Get list of supported insurance providers"""
        response = requests.get(f"{self.base_url}/supported-insurers")
        return response.json()
    
    def parse_pdf_file(self, file_path: str, insurer: str = "auto"):
        """
        Parse a PDF file by uploading it
        
        Args:
            file_path: Path to PDF file
            insurer: Insurance provider (auto, discovery, santam, etc.)
        
        Returns:
            Parsed policy data as dictionary
        """
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'application/pdf')}
            params = {'insurer': insurer}
            
            response = requests.post(
                f"{self.base_url}/parse",
                files=files,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Error: {response.status_code} - {response.text}")
    
    def parse_from_path(self, file_path: str, insurer: str = "auto"):
        """
        Parse a PDF from a server-side path
        
        Args:
            file_path: Absolute path to PDF file on server
            insurer: Insurance provider
        
        Returns:
            Parsed policy data as dictionary
        """
        response = requests.post(
            f"{self.base_url}/parse-from-path",
            params={'filepath': file_path, 'insurer': insurer}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = InsurancePolicyParserClient("http://localhost:8000")
    
    # Check health
    print("=== Health Check ===")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    print()
    
    # Get supported insurers
    print("=== Supported Insurers ===")
    insurers = client.get_supported_insurers()
    print(json.dumps(insurers, indent=2))
    print()
    
    # Parse a PDF file (upload method)
    print("=== Parsing PDF (Upload) ===")
    pdf_path = "/mnt/user-data/uploads/noQId_Discovery_Insure_Plan_Schedule_-_2022_unlocked.pdf"
    
    try:
        result = client.parse_pdf_file(pdf_path, insurer="auto")
        
        # Print summary
        print(f"Planholder: {result['planholder']['name']}")
        print(f"Plan Number: {result['planNumber']}")
        print(f"Monthly Premium: R{result['currentMonthlyPremium']}")
        print(f"Number of Vehicles: {len(result['motorVehicles'])}")
        print(f"Number of Buildings: {len(result['buildings'])}")
        print()
        
        # Save full result
        with open('/mnt/user-data/outputs/api_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("Full result saved to api_result.json")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example: Parse from server path
    print("\n=== Parsing PDF (Server Path) ===")
    try:
        result = client.parse_from_path(pdf_path, insurer="discovery")
        print(f"Successfully parsed: {result['planNumber']}")
    except Exception as e:
        print(f"Error: {e}")


# JavaScript/TypeScript equivalent
JAVASCRIPT_EXAMPLE = '''
// JavaScript/TypeScript example
async function parsePolicyPDF(filePath) {
    const formData = new FormData();
    const fileBlob = await fetch(filePath).then(r => r.blob());
    formData.append('file', fileBlob, 'policy.pdf');
    
    const response = await fetch('http://localhost:8000/parse?insurer=auto', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

// Usage
parsePolicyPDF('/path/to/policy.pdf')
    .then(data => {
        console.log('Planholder:', data.planholder.name);
        console.log('Monthly Premium:', data.currentMonthlyPremium);
    })
    .catch(error => console.error('Error:', error));
'''

# cURL example
CURL_EXAMPLE = '''
# Upload and parse a PDF
curl -X POST "http://localhost:8000/parse?insurer=auto" \\
  -H "accept: application/json" \\
  -H "Content-Type: multipart/form-data" \\
  -F "file=@/path/to/policy.pdf"

# Parse from server path
curl -X POST "http://localhost:8000/parse-from-path?filepath=/path/to/policy.pdf&insurer=discovery" \\
  -H "accept: application/json"
'''

if __name__ == "__main__":
    print("\n" + "="*60)
    print("JavaScript/TypeScript Example:")
    print("="*60)
    print(JAVASCRIPT_EXAMPLE)
    
    print("\n" + "="*60)
    print("cURL Example:")
    print("="*60)
    print(CURL_EXAMPLE)
