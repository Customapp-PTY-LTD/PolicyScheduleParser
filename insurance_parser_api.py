#!/usr/bin/env python3
"""
Insurance Policy Schedule Parser Web Service
Supports multiple insurance providers with a pluggable parser architecture
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
from typing import Dict, Optional
from pathlib import Path
import logging
from enum import Enum
import pdfplumber
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Insurance Policy Parser API",
    description="Extract structured data from insurance policy schedule PDFs",
    version="1.0.0"
)


class InsurerType(str, Enum):
    """Supported insurance providers"""
    DISCOVERY = "discovery"
    SANTAM = "santam"
    OLD_MUTUAL = "old_mutual"
    OUTSURANCE = "outsurance"
    AUTO = "auto"  # Auto-detect


class BaseParser:
    """Base class for insurance policy parsers"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pages_text = {}
        
    def extract_text(self):
        """Extract text from all pages"""
        with pdfplumber.open(self.pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                self.pages_text[i] = page.extract_text()
    
    def identify_insurer(self) -> str:
        """Identify the insurance company from the document"""
        raise NotImplementedError
    
    def parse(self) -> Dict:
        """Parse the document and return structured data"""
        raise NotImplementedError


class DiscoveryParser(BaseParser):
    """Parser for Discovery Insure policy schedules"""
    
    def identify_insurer(self) -> str:
        """Check if this is a Discovery document"""
        page1 = self.pages_text.get(1, "") + self.pages_text.get(2, "")
        if "Discovery Insure" in page1:
            return "discovery"
        return None
    
    def parse(self) -> Dict:
        """Parse Discovery Insure policy schedule"""
        policy = {
            "insurer": "Discovery Insure",
            "planNumber": None,
            "planType": None,
            "quoteEffectiveDate": None,
            "commencementDate": None,
            "planholder": {},
            "payment": {},
            "motorVehicles": [],
            "buildings": [],
            "householdContents": None,
            "personalLiability": None,
            "currentMonthlyPremium": None,
            "additionalBenefits": {}
        }
        
        # Parse different sections
        self._parse_header_info(policy)
        self._parse_planholder_details(policy)
        self._parse_payment_details(policy)
        self._parse_summary_of_cover(policy)
        self._parse_motor_vehicles(policy)
        self._parse_buildings(policy)
        self._parse_household_contents(policy)
        self._parse_personal_liability(policy)
        
        return policy
    
    def _parse_header_info(self, policy: Dict):
        """Extract plan header information"""
        page2 = self.pages_text.get(2, "")
        
        match = re.search(r'Plan number\s+(\d+)', page2)
        if match:
            policy["planNumber"] = match.group(1)
        
        match = re.search(r'Plan type:\s+(\w+)', page2)
        if match:
            policy["planType"] = match.group(1)
        
        match = re.search(r'Quote effective date:\s+(\d{2}/\d{2}/\d{4})', page2)
        if match:
            policy["quoteEffectiveDate"] = match.group(1)
        
        match = re.search(r'Commencement date:\s+(\d{2}/\d{2}/\d{4})', page2)
        if match:
            policy["commencementDate"] = match.group(1)
    
    def _parse_planholder_details(self, policy: Dict):
        """Extract planholder information"""
        page2 = self.pages_text.get(2, "")
        
        planholder = {
            "name": None,
            "idNumber": None,
            "dateOfBirth": None,
            "maritalStatus": None,
            "residentialAddress": {},
            "contact": {}
        }
        
        match = re.search(r'Planholder\s+([^\n]+?)\s+Planholder type', page2)
        if match:
            planholder["name"] = match.group(1).strip()
        
        match = re.search(r'Identity/passport number\s+(\d+)', page2)
        if match:
            planholder["idNumber"] = match.group(1)
        
        match = re.search(r'Date of birth\s+(\d{2}/\d{2}/\d{4})', page2)
        if match:
            planholder["dateOfBirth"] = match.group(1)
        
        match = re.search(r'Marital status\s+(\w+)', page2)
        if match:
            planholder["maritalStatus"] = match.group(1)
        
        match = re.search(r'Email address\s+([^\s]+@[^\s]+)', page2)
        if match:
            planholder["contact"]["email"] = match.group(1)
        
        match = re.search(r'Cellphone number\s+(\d+)', page2)
        if match:
            planholder["contact"]["cellphone"] = match.group(1)
        
        policy["planholder"] = planholder
    
    def _parse_payment_details(self, policy: Dict):
        """Extract payment information"""
        page3 = self.pages_text.get(3, "")
        
        payment = {
            "paymentType": "Debit Order" if "Debit Order" in page3 else None,
            "accountHolder": None,
            "bank": None,
            "accountType": None,
            "branchCode": None,
            "debitDay": None,
            "paymentFrequency": None
        }
        
        match = re.search(r'Account holder\s+(.+?)\s+Account number', page3)
        if match:
            payment["accountHolder"] = match.group(1).strip()
        
        match = re.search(r'Financial institution\s+(.+?)\s+Account type', page3)
        if match:
            payment["bank"] = match.group(1).strip()
        
        match = re.search(r'Account type\s+(\w+)', page3)
        if match:
            payment["accountType"] = match.group(1)
        
        match = re.search(r'Branch name and code\s+Branch \d+\s+(\d+)', page3)
        if match:
            payment["branchCode"] = match.group(1)
        
        match = re.search(r'Debit day\s+(\d+)', page3)
        if match:
            payment["debitDay"] = int(match.group(1))
        
        match = re.search(r'Payment frequency\s+(\w+)', page3)
        if match:
            payment["paymentFrequency"] = match.group(1)
        
        policy["payment"] = payment
    
    def _parse_summary_of_cover(self, policy: Dict):
        """Extract summary and monthly premium"""
        page4 = self.pages_text.get(4, "")
        
        match = re.search(r'Current monthly premium\s+R\s*([\d\s,]+\.\d{2})', page4)
        if match:
            premium_str = match.group(1).replace(' ', '').replace(',', '')
            policy["currentMonthlyPremium"] = float(premium_str)
        
        match = re.search(r'SASRIA\s+R([\d.]+)', page4)
        if match:
            policy["additionalBenefits"]["sasria"] = float(match.group(1))
        
        match = re.search(r'Vitalitydrive.*?R([\d.]+)', page4)
        if match:
            policy["additionalBenefits"]["vitalitydrive"] = float(match.group(1))
    
    def _parse_motor_vehicles(self, policy: Dict):
        """Extract motor vehicle information"""
        vehicles = []
        
        for page_num in range(6, 12):
            page_text = self.pages_text.get(page_num, "")
            
            match = re.search(r'(\d+)\.\s+([A-Z-]+),\s+([A-Z0-9\s/]+?)\s+Registration\s+(\w+)', page_text)
            if match:
                vehicle = {
                    "vehicleNumber": int(match.group(1)),
                    "make": match.group(2),
                    "model": match.group(3).strip(),
                    "registration": match.group(4),
                    "primaryDriver": None,
                    "premium": None,
                    "excess": {},
                    "details": {}
                }
                
                driver_match = re.search(r'Primary driver details:\s+(.+)', page_text)
                if driver_match:
                    vehicle["primaryDriver"] = driver_match.group(1).strip()
                
                premium_match = re.search(r'Total\s+R([\d,]+\.\d{2})', page_text)
                if premium_match:
                    vehicle["premium"] = float(premium_match.group(1).replace(',', ''))
                
                excess_match = re.search(r'Excess motor.*?Basic\s+R([\d,]+\.\d{2}).*?Total\s+R([\d,]+\.\d{2})', page_text, re.DOTALL)
                if excess_match:
                    vehicle["excess"] = {
                        "basic": float(excess_match.group(1).replace(',', '')),
                        "total": float(excess_match.group(2).replace(',', ''))
                    }
                
                year_match = re.search(r'Year of manufacture\s+(\d{4})', page_text)
                if year_match:
                    vehicle["details"]["yearOfManufacture"] = int(year_match.group(1))
                
                vin_match = re.search(r'VIN number\s+([A-Z0-9]+)', page_text)
                if vin_match:
                    vehicle["details"]["vinNumber"] = vin_match.group(1)
                
                vehicles.append(vehicle)
        
        policy["motorVehicles"] = vehicles
    
    def _parse_buildings(self, policy: Dict):
        """Extract building information"""
        buildings = []
        
        for page_num in range(12, 16):
            page_text = self.pages_text.get(page_num, "")
            
            if "Buildings" in page_text and re.search(r'\d+\.\s+.+', page_text):
                building = {
                    "address": None,
                    "effectiveDate": None,
                    "sumInsured": None,
                    "premium": None,
                    "coverType": "Comprehensive"
                }
                
                addr_match = re.search(r'\d+\.\s+(.+?)\s+(?:Registration|Plan details)', page_text)
                if addr_match:
                    building["address"] = addr_match.group(1).strip()
                
                sum_match = re.search(r'Sum insured.*?R\s*([\d,\s]+\.\d{2})', page_text, re.DOTALL)
                if sum_match:
                    sum_str = sum_match.group(1).replace(',', '').replace(' ', '')
                    building["sumInsured"] = float(sum_str)
                
                prem_match = re.search(r'Premium\s+R([\d.]+)', page_text)
                if prem_match:
                    building["premium"] = float(prem_match.group(1))
                
                date_match = re.search(r'Effective date:\s+(\d{2}/\d{2}/\d{4})', page_text)
                if date_match:
                    building["effectiveDate"] = date_match.group(1)
                
                if building["address"]:
                    buildings.append(building)
        
        policy["buildings"] = buildings
    
    def _parse_household_contents(self, policy: Dict):
        """Extract household contents information"""
        for page_num in range(16, 18):
            page_text = self.pages_text.get(page_num, "")
            
            if "Household contents" in page_text:
                contents = {
                    "address": None,
                    "sumInsured": None,
                    "premium": None
                }
                
                sum_match = re.search(r'Sum insured.*?R\s*([\d,\s]+\.\d{2})', page_text, re.DOTALL)
                if sum_match:
                    sum_str = sum_match.group(1).replace(',', '').replace(' ', '')
                    contents["sumInsured"] = float(sum_str)
                
                prem_match = re.search(r'Total.*?R([\d,.]+)', page_text, re.DOTALL)
                if prem_match:
                    contents["premium"] = float(prem_match.group(1).replace(',', ''))
                
                policy["householdContents"] = contents
                break
    
    def _parse_personal_liability(self, policy: Dict):
        """Extract personal liability information"""
        for page_num in range(18, 20):
            page_text = self.pages_text.get(page_num, "")
            
            if "Personal liability" in page_text:
                liability = {
                    "sumInsured": None,
                    "premium": None
                }
                
                sum_match = re.search(r'Sum insured.*?R([\d,]+\.\d{2})', page_text, re.DOTALL)
                if sum_match:
                    liability["sumInsured"] = float(sum_match.group(1).replace(',', ''))
                
                prem_match = re.search(r'Premium.*?R([\d.]+)', page_text, re.DOTALL)
                if prem_match:
                    liability["premium"] = float(prem_match.group(1))
                
                policy["personalLiability"] = liability
                break


class SantamParser(BaseParser):
    """Parser for Santam policy schedules (stub - to be implemented)"""
    
    def identify_insurer(self) -> str:
        page1 = self.pages_text.get(1, "")
        if "Santam" in page1:
            return "santam"
        return None
    
    def parse(self) -> Dict:
        return {
            "insurer": "Santam",
            "error": "Santam parser not yet implemented"
        }


class GenericParser(BaseParser):
    """Generic fallback parser for unknown formats"""
    
    def identify_insurer(self) -> str:
        return "unknown"
    
    def parse(self) -> Dict:
        """Basic extraction when insurer not recognized"""
        return {
            "insurer": "Unknown",
            "rawText": {
                f"page{i}": text[:500] + "..." if len(text) > 500 else text
                for i, text in list(self.pages_text.items())[:3]
            },
            "message": "Insurance provider not recognized. Returning raw text from first 3 pages."
        }


class ParserFactory:
    """Factory to create appropriate parser based on insurer"""
    
    PARSERS = {
        InsurerType.DISCOVERY: DiscoveryParser,
        InsurerType.SANTAM: SantamParser,
    }
    
    @staticmethod
    def create_parser(pdf_path: str, insurer_type: InsurerType = InsurerType.AUTO) -> BaseParser:
        """Create appropriate parser for the document"""
        
        if insurer_type == InsurerType.AUTO:
            # Auto-detect insurer
            temp_parser = GenericParser(pdf_path)
            temp_parser.extract_text()
            
            # Try each parser's identification
            for parser_class in [DiscoveryParser, SantamParser]:
                parser = parser_class(pdf_path)
                parser.pages_text = temp_parser.pages_text
                if parser.identify_insurer():
                    return parser
            
            # Fallback to generic parser
            return temp_parser
        
        # Use specified parser
        parser_class = ParserFactory.PARSERS.get(insurer_type, GenericParser)
        return parser_class(pdf_path)


# API Endpoints

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "Insurance Policy Parser API",
        "version": "1.0.0"
    }


@app.get("/supported-insurers")
async def supported_insurers():
    """Get list of supported insurance providers"""
    return {
        "supported": [
            {"id": "discovery", "name": "Discovery Insure", "status": "fully_supported"},
            {"id": "santam", "name": "Santam", "status": "coming_soon"},
            {"id": "old_mutual", "name": "Old Mutual", "status": "coming_soon"},
            {"id": "outsurance", "name": "Outsurance", "status": "coming_soon"},
        ],
        "auto_detect": True
    }


@app.post("/parse")
async def parse_policy(
    file: UploadFile = File(...),
    insurer: Optional[InsurerType] = InsurerType.AUTO
):
    """
    Parse an insurance policy schedule PDF
    
    Args:
        file: PDF file to parse
        insurer: Insurance provider (auto-detect by default)
    
    Returns:
        Structured JSON data extracted from the policy
    """
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_path = tmp_file.name
        content = await file.read()
        tmp_file.write(content)
    
    try:
        logger.info(f"Processing file: {file.filename}, size: {len(content)} bytes")
        
        # Create appropriate parser
        parser = ParserFactory.create_parser(tmp_path, insurer)
        parser.extract_text()
        
        # Parse the document
        result = parser.parse()
        
        logger.info(f"Successfully parsed {file.filename}")
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error parsing {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")
        
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/parse-from-path")
async def parse_from_path(filepath: str, insurer: Optional[InsurerType] = InsurerType.AUTO):
    """
    Parse an insurance policy schedule from a file path
    
    Args:
        filepath: Absolute path to PDF file
        insurer: Insurance provider (auto-detect by default)
    
    Returns:
        Structured JSON data extracted from the policy
    """
    
    # Validate file exists
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File not found: {filepath}")
    
    if not filepath.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        logger.info(f"Processing file from path: {filepath}")
        
        # Create appropriate parser
        parser = ParserFactory.create_parser(filepath, insurer)
        parser.extract_text()
        
        # Parse the document
        result = parser.parse()
        
        logger.info(f"Successfully parsed {filepath}")
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error parsing {filepath}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
