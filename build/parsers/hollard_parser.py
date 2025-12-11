"""
Hollard Insurance Policy Schedule Parser
Extracts data from Hollard Private Portfolio policy schedule PDFs
"""

import re
from typing import Dict, List, Optional
from .base_parser import BaseParser


class HollardParser(BaseParser):
    """
    Parser for Hollard Insurance policy schedules.
    
    Handles extraction of:
    - Policyholder details
    - Broker and administrator information
    - Premium schedule and sections
    - Household contents
    - All risks items
    - Personal liability
    - Motor vehicles (multiple)
    - Driver details
    """
    
    @classmethod
    def get_document_name(cls) -> str:
        return "Hollard Private Portfolio Policy Schedule"
    
    @classmethod
    def get_supported_fields(cls) -> list:
        return [
            "quoteNumber", "policyType", "periodOfInsurance", "startDate",
            "policyholder", "broker", "insurer", "administrator",
            "premiumSchedule", "householdContents", "allRisks",
            "personalLiability", "motorVehicles", "totalPremium"
        ]
    
    def identify_document(self) -> bool:
        """Check if this is a Hollard document"""
        all_text = " ".join(self.pages_text.values())
        return "HOLLARD" in all_text.upper() and ("PRIVATE PORTFOLIO" in all_text.upper() or "HOLLARD INSURANCE" in all_text.upper())
    
    def parse(self) -> Dict:
        """Parse Hollard policy schedule"""
        policy = {
            "insurer": "Hollard Insurance",
            "documentType": "Private Portfolio",
            "quoteNumber": None,
            "policyType": None,
            "periodOfInsurance": None,
            "startDate": None,
            "policyholder": {},
            "broker": {},
            "insurerDetails": {},
            "administrator": {},
            "premiumSchedule": {},
            "householdContents": [],
            "allRisks": [],
            "personalLiability": None,
            "motorVehicles": [],
            "totalPremium": None,
            "totalFees": None,
            "sasria": None,
            "grandTotal": None
        }
        
        # Parse different sections
        self._parse_policy_details(policy)
        self._parse_policyholder(policy)
        self._parse_broker_details(policy)
        self._parse_insurer_details(policy)
        self._parse_administrator_details(policy)
        self._parse_premium_schedule(policy)
        self._parse_household_contents(policy)
        self._parse_all_risks(policy)
        self._parse_personal_liability(policy)
        self._parse_motor_vehicles(policy)
        
        return policy
    
    def _parse_policy_details(self, policy: Dict):
        """Extract policy header information"""
        all_text = self._get_all_text()
        
        # Quote number
        match = re.search(r'Quote number.*?:\s*([A-Z0-9-]+)', all_text, re.IGNORECASE)
        if match:
            policy["quoteNumber"] = match.group(1).strip()
        
        # Policy type
        match = re.search(r'Type of policy\s*:\s*(\w+)', all_text, re.IGNORECASE)
        if match:
            policy["policyType"] = match.group(1)
        
        # Period of insurance
        match = re.search(r'Period of insurance\s*:\s*\(A\)\s*([^\n]+)', all_text)
        if match:
            policy["periodOfInsurance"] = match.group(1).strip()
        
        # Start date
        match = re.search(r'Start date\s*:\s*(\d{2}/\d{2}/\d{4})', all_text)
        if match:
            policy["startDate"] = match.group(1)
        else:
            # Alternative format
            match = re.search(r'Start date\s*:\s*(\d{1,2}\s+\w+\s+\d{4})', all_text)
            if match:
                policy["startDate"] = match.group(1)
    
    def _parse_policyholder(self, policy: Dict):
        """Extract policyholder information"""
        all_text = self._get_all_text()
        
        policyholder = {
            "name": None,
            "address": {
                "physical": None,
                "postal": None
            },
            "contact": {
                "work": None,
                "home": None,
                "fax": None,
                "cell": None,
                "email": None
            },
            "dateOfBirth": None
        }
        
        # Name
        match = re.search(r'The policyholder\s*:\s*([^\n]+)', all_text)
        if match:
            policyholder["name"] = match.group(1).strip()
        
        # Physical address - look for Address details section
        match = re.search(r'Address details\s*:\s*Physical\s+([^\n]+(?:\n[^\n]+)*?)(?:\nContact|Postal)', all_text, re.DOTALL)
        if match:
            addr_lines = match.group(1).strip().split('\n')
            policyholder["address"]["physical"] = ', '.join(line.strip() for line in addr_lines if line.strip())
        
        # Cell phone
        match = re.search(r':\s*Cell\s+(\d[\d\s]+)', all_text)
        if match:
            policyholder["contact"]["cell"] = match.group(1).strip().replace(' ', '')
        
        # Email
        match = re.search(r':\s*E-mail\s+([^\s\n]+@[^\s\n]+)', all_text)
        if match:
            policyholder["contact"]["email"] = match.group(1).strip()
        
        # Date of birth
        match = re.search(r'Date of Birth\s*:\s*(\d{2}/\d{2}/\d{4})', all_text)
        if match:
            policyholder["dateOfBirth"] = match.group(1)
        
        policy["policyholder"] = policyholder
    
    def _parse_broker_details(self, policy: Dict):
        """Extract broker information"""
        all_text = self._get_all_text()
        
        broker = {
            "company": None,
            "branch": None,
            "address": None,
            "contact": {
                "tel": None,
                "fax": None,
                "email": None
            },
            "registrationNumber": None,
            "vatNumber": None,
            "fspLicence": None
        }
        
        # Find broker section
        broker_section = re.search(r'Broker details(.*?)(?:Insurer details|$)', all_text, re.DOTALL | re.IGNORECASE)
        if broker_section:
            section = broker_section.group(1)
            
            match = re.search(r'Company\s*:\s*([^\n]+)', section)
            if match:
                broker["company"] = match.group(1).strip()
            
            match = re.search(r'Branch\s*:\s*([^\n]+)', section)
            if match:
                broker["branch"] = match.group(1).strip()
            
            match = re.search(r'Tel\s+([^\n]+)', section)
            if match:
                broker["contact"]["tel"] = match.group(1).strip()
            
            match = re.search(r'E-mail\s+([^\s\n]+@[^\s\n]+)', section)
            if match:
                broker["contact"]["email"] = match.group(1).strip()
            
            match = re.search(r'Licence Number\s+(\d+)', section)
            if match:
                broker["fspLicence"] = match.group(1)
        
        policy["broker"] = broker
    
    def _parse_insurer_details(self, policy: Dict):
        """Extract insurer information"""
        all_text = self._get_all_text()
        
        insurer = {
            "company": None,
            "address": None,
            "contact": {
                "tel": None,
                "email": None,
                "website": None
            },
            "registrationNumber": None,
            "fspLicence": None
        }
        
        # Find insurer section
        insurer_section = re.search(r'Insurer details(.*?)(?:DETAILS OF ADMINISTRATOR|$)', all_text, re.DOTALL | re.IGNORECASE)
        if insurer_section:
            section = insurer_section.group(1)
            
            match = re.search(r'Company\s*:\s*([^\n]+)', section)
            if match:
                insurer["company"] = match.group(1).strip()
            
            match = re.search(r'Tel\s+([^\n]+)', section)
            if match:
                insurer["contact"]["tel"] = match.group(1).strip()
            
            match = re.search(r'Website\s+([^\s\n]+)', section)
            if match:
                insurer["contact"]["website"] = match.group(1).strip()
            
            match = re.search(r'Licence Number\s+(\d+)', section)
            if match:
                insurer["fspLicence"] = match.group(1)
        
        policy["insurerDetails"] = insurer
    
    def _parse_administrator_details(self, policy: Dict):
        """Extract administrator information"""
        all_text = self._get_all_text()
        
        admin = {
            "company": None,
            "address": None,
            "contact": {
                "tel": None,
                "email": None,
                "website": None
            },
            "fspLicence": None
        }
        
        # Find admin section
        admin_section = re.search(r'DETAILS OF ADMINISTRATOR(.*?)(?:PREMIUM SCHEDULE|Print date)', all_text, re.DOTALL | re.IGNORECASE)
        if admin_section:
            section = admin_section.group(1)
            
            match = re.search(r'Company\s*:\s*([^\n]+)', section)
            if match:
                admin["company"] = match.group(1).strip()
            
            match = re.search(r'Work\s+([^\n]+)', section)
            if match:
                admin["contact"]["tel"] = match.group(1).strip()
            
            match = re.search(r'E-mail\s+([^\s\n]+@[^\s\n]+)', section)
            if match:
                admin["contact"]["email"] = match.group(1).strip()
            
            match = re.search(r'Website\s+([^\s\n]+)', section)
            if match:
                admin["contact"]["website"] = match.group(1).strip()
            
            match = re.search(r'Licence Number\s+(\d+)', section)
            if match:
                admin["fspLicence"] = match.group(1)
        
        policy["administrator"] = admin
    
    def _parse_premium_schedule(self, policy: Dict):
        """Extract premium schedule and totals"""
        all_text = self._get_all_text()
        
        schedule = {
            "sections": [],
            "totalPremium": None,
            "totalFees": None,
            "insurancePayment": None,
            "sasria": None,
            "subtotal": None,
            "additionalServices": None,
            "grandTotal": None,
            "vatAmount": None,
            "commissionAmount": None
        }
        
        # Find premium schedule section
        sched_section = re.search(r'PREMIUM SCHEDULE AND INDEX OF COVER(.*?)(?:NOTE TO POLICYHOLDER|ACCEPTANCE)', all_text, re.DOTALL)
        if sched_section:
            section = sched_section.group(1)
            
            # Parse individual sections
            section_pattern = r'(\d+)\s+([\w\s-]+?)\s+(YES|NO)\s+(YES|NO)\s+(?:R\s*)?([\d\s,]+|-)\s+R\s*([\d\s,.]+|-)\s+R?\s*([\d\s,.]+|-)'
            for match in re.finditer(section_pattern, section):
                sec = {
                    "number": int(match.group(1)),
                    "name": match.group(2).strip(),
                    "included": match.group(3) == "YES",
                    "sasriaIncluded": match.group(4) == "YES",
                    "sumInsured": self._clean_amount(match.group(5)),
                    "prorata": self._clean_amount(match.group(6)),
                    "monthlyPremium": self._clean_amount(match.group(7))
                }
                if sec["included"]:
                    schedule["sections"].append(sec)
            
            # Extract totals - handle multiple number patterns
            # Total Premium line: "Total Premium R - R 3 236.75"
            match = re.search(r'Total Premium\s+R\s*-?\s*R\s*([\d\s,.]+)', section)
            if match:
                schedule["totalPremium"] = self._clean_amount(match.group(1))
            
            # Total Fees line
            match = re.search(r'Total Fees\s+R\s*-?\s*R\s*([\d\s,.]+)', section)
            if match:
                schedule["totalFees"] = self._clean_amount(match.group(1))
            
            # Insurance Payment line
            match = re.search(r'Insurance Payment\s+R\s*-?\s*R\s*([\d\s,.]+)', section)
            if match:
                schedule["insurancePayment"] = self._clean_amount(match.group(1))
            
            # Sasria line
            match = re.search(r'Sasria\s+R\s*-?\s*R\s*([\d\s,.]+)', section)
            if match:
                schedule["sasria"] = self._clean_amount(match.group(1))
                
            # Additional Services
            match = re.search(r'Additional Services.*?R\s*-?\s*R\s*([\d\s,.]+)', section)
            if match:
                schedule["additionalServices"] = self._clean_amount(match.group(1))
            
            # Grand Total - the last TOTAL line
            match = re.search(r'TOTAL\s+R\s*-?\s*R\s*([\d\s,.]+)', section)
            if match:
                schedule["grandTotal"] = self._clean_amount(match.group(1))
        
        # Extract VAT and Commission from note
        match = re.search(r'VAT of R([\d,.]+)', all_text)
        if match:
            schedule["vatAmount"] = self._clean_amount(match.group(1))
        
        match = re.search(r'Commission of R([\d,.]+)', all_text)
        if match:
            schedule["commissionAmount"] = self._clean_amount(match.group(1))
        
        policy["premiumSchedule"] = schedule
        policy["totalPremium"] = schedule["totalPremium"]
        policy["totalFees"] = schedule["totalFees"]
        policy["sasria"] = schedule["sasria"]
        policy["grandTotal"] = schedule["grandTotal"]
    
    def _parse_household_contents(self, policy: Dict):
        """Extract household contents information"""
        all_text = self._get_all_text()
        contents_list = []
        
        # Find all household contents sections
        for page_num, page_text in self.pages_text.items():
            if "HOUSEHOLD CONTENTS" in page_text and "Item Reference" in page_text:
                contents = {
                    "itemReference": None,
                    "riskAddress": None,
                    "startDate": None,
                    "sumInsured": None,
                    "premium": None,
                    "typeOfHome": None,
                    "locality": None,
                    "wallConstruction": None,
                    "roofConstruction": None,
                    "occupancy": None,
                    "coverOption": None,
                    "sasriaIncluded": False,
                    "sasriaPremium": None,
                    "basicExcess": None,
                    "securityMeasures": None,
                    "additionalCover": {}
                }
                
                # Item reference
                match = re.search(r'Item Reference\s*:\s*(\w+)', page_text)
                if match:
                    contents["itemReference"] = match.group(1)
                
                # Risk address
                match = re.search(r'RISK ADDRESS\s*:\s*([^\n]+(?:\n[^\n]+)*?)(?:\nRISK DETAILS|\nStart)', page_text, re.DOTALL)
                if match:
                    contents["riskAddress"] = match.group(1).replace('\n', ', ').strip()
                
                # Start date
                match = re.search(r'Start date\s*:\s*(\d{1,2}\s+\w+\s+\d{4})', page_text)
                if match:
                    contents["startDate"] = match.group(1)
                
                # Sum insured and premium from the header line
                match = re.search(r'Start date\s*:\s*\d{1,2}\s+\w+\s+\d{4}\s+([\d\s,]+)\s+([\d,.]+)', page_text)
                if match:
                    contents["sumInsured"] = self._clean_amount(match.group(1))
                    contents["premium"] = self._clean_amount(match.group(2))
                
                # Type of home
                match = re.search(r'Type of home\s*:\s*([^\n]+)', page_text)
                if match:
                    contents["typeOfHome"] = match.group(1).strip()
                
                # Locality
                match = re.search(r'Locality\s*:\s*([^\n]+)', page_text)
                if match:
                    contents["locality"] = match.group(1).strip()
                
                # Wall construction
                match = re.search(r'Wall construction\s*:\s*(\w+)', page_text)
                if match:
                    contents["wallConstruction"] = match.group(1)
                
                # Roof construction
                match = re.search(r'Roof construction\s*:\s*(\w+)', page_text)
                if match:
                    contents["roofConstruction"] = match.group(1)
                
                # Occupancy
                match = re.search(r'Occupancy\s*:\s*([^\n]+)', page_text)
                if match:
                    contents["occupancy"] = match.group(1).strip()
                
                # Cover option
                match = re.search(r'Cover option\s*:\s*([^\n]+)', page_text)
                if match:
                    contents["coverOption"] = match.group(1).strip()
                
                # SASRIA
                if re.search(r'Sasria included\s*:\s*Yes', page_text, re.IGNORECASE):
                    contents["sasriaIncluded"] = True
                    match = re.search(r'Sasria included\s*:\s*Yes\s+([\d,.]+)', page_text)
                    if match:
                        contents["sasriaPremium"] = self._clean_amount(match.group(1))
                
                # Basic excess
                match = re.search(r'Basic excess\s*:\s*R\s*([\d\s,]+)', page_text)
                if match:
                    contents["basicExcess"] = self._clean_amount(match.group(1))
                
                # Security measures
                match = re.search(r'Minimum security measures\s*:\s*([^\n]+)', page_text)
                if match:
                    contents["securityMeasures"] = match.group(1).strip()
                
                # Additional covers
                if "Accidental damage" in page_text:
                    match = re.search(r'Accidental damage.*?:\s*Yes\s+([\d\s,]+)\s+([\d,.]+)', page_text)
                    if match:
                        contents["additionalCover"]["accidentalDamage"] = {
                            "sumInsured": self._clean_amount(match.group(1)),
                            "premium": self._clean_amount(match.group(2))
                        }
                
                if "Power surge" in page_text:
                    match = re.search(r'Power surge\s*:\s*Yes\s+([\d\s,]+)\s+([\d,.]+)', page_text)
                    if match:
                        contents["additionalCover"]["powerSurge"] = {
                            "sumInsured": self._clean_amount(match.group(1)),
                            "premium": self._clean_amount(match.group(2))
                        }
                
                # Total
                match = re.search(r'TOTAL\s+([\d,.]+)', page_text)
                if match:
                    contents["totalPremium"] = self._clean_amount(match.group(1))
                
                if contents["itemReference"]:
                    contents_list.append(contents)
        
        policy["householdContents"] = contents_list
    
    def _parse_all_risks(self, policy: Dict):
        """Extract all risks items"""
        all_text = self._get_all_text()
        all_risks = []
        
        # Find all risks section
        for page_num, page_text in self.pages_text.items():
            if "ALL RISKS" in page_text and "Item #" in page_text:
                # Parse items
                item_pattern = r'(\w+)\s+([\w/\s]+?)\s+([\w/\s()]+?)\s+([\d\s,]+)\s+([\d,.]+)'
                for match in re.finditer(item_pattern, page_text):
                    item = {
                        "itemNumber": match.group(1),
                        "category": match.group(2).strip(),
                        "description": match.group(3).strip(),
                        "sumInsured": self._clean_amount(match.group(4)),
                        "premium": self._clean_amount(match.group(5))
                    }
                    
                    # Only add if it looks like a valid item
                    if item["itemNumber"].startswith("ALL"):
                        all_risks.append(item)
                
                # Also try simpler pattern
                if not all_risks:
                    match = re.search(r'ALL\d+\s+.*?Unspecified.*?\s+([\d\s,]+)\s+([\d,.]+)', page_text)
                    if match:
                        item = {
                            "itemNumber": "ALL0001",
                            "category": "Clothing/Personal Effects",
                            "description": "Unspecified",
                            "sumInsured": self._clean_amount(match.group(1)),
                            "premium": self._clean_amount(match.group(2))
                        }
                        all_risks.append(item)
        
        policy["allRisks"] = all_risks
    
    def _parse_personal_liability(self, policy: Dict):
        """Extract personal liability information"""
        all_text = self._get_all_text()
        
        liability = {
            "itemReference": None,
            "startDate": None,
            "sumInsured": None,
            "premium": None,
            "businessLiability": False
        }
        
        # Find personal liability section
        for page_num, page_text in self.pages_text.items():
            if "PERSONAL LIABILITY" in page_text and "Item Reference" in page_text:
                match = re.search(r'Item Reference\s*:\s*(\w+)', page_text)
                if match:
                    liability["itemReference"] = match.group(1)
                
                match = re.search(r'Start date\s*:\s*(\d{1,2}\s+\w+\s+\d{4})', page_text)
                if match:
                    liability["startDate"] = match.group(1)
                
                match = re.search(r'Personal Liability\s+([\d\s,]+)\s+([\d,.]+)', page_text)
                if match:
                    liability["sumInsured"] = self._clean_amount(match.group(1))
                    liability["premium"] = self._clean_amount(match.group(2))
                
                if re.search(r'Business Liability\s*:\s*Yes', page_text, re.IGNORECASE):
                    liability["businessLiability"] = True
                
                break
        
        policy["personalLiability"] = liability
    
    def _parse_motor_vehicles(self, policy: Dict):
        """Extract motor vehicle information"""
        vehicles = []
        page_nums = sorted(self.pages_text.keys())
        
        for page_num in page_nums:
            page_text = self.pages_text[page_num]
            if "MOTOR" in page_text and "Item Reference" in page_text and "Make" in page_text:
                vehicle = self._parse_single_vehicle(page_text, page_num)
                if vehicle and vehicle.get("make"):
                    # Check if this vehicle is already added (by registration)
                    existing = any(v.get("registration") == vehicle.get("registration") for v in vehicles)
                    if not existing:
                        # Look for driver details on this page or the next page
                        self._extract_driver_details(vehicle, page_num, page_nums)
                        vehicles.append(vehicle)
        
        policy["motorVehicles"] = vehicles
    
    def _extract_driver_details(self, vehicle: Dict, page_num: int, page_nums: list):
        """Extract driver details from current or next page"""
        # First try current page
        page_text = self.pages_text.get(page_num, "")
        driver_found = self._parse_driver_from_text(vehicle, page_text)
        
        # If not found, try the next page
        if not driver_found:
            idx = page_nums.index(page_num)
            if idx + 1 < len(page_nums):
                next_page_text = self.pages_text.get(page_nums[idx + 1], "")
                self._parse_driver_from_text(vehicle, next_page_text)
    
    def _parse_driver_from_text(self, vehicle: Dict, page_text: str) -> bool:
        """Parse driver information from page text"""
        # Check if driver details section exists
        if "Driver Name" not in page_text:
            return False
        
        match = re.search(r'Driver Name\s*:\s*([^\n]+)', page_text)
        if match:
            vehicle["driver"]["name"] = match.group(1).strip()
        
        match = re.search(r'Date of Birth\s*:\s*(\d{1,2}\s+\w+\s+\d{4})', page_text)
        if match:
            vehicle["driver"]["dateOfBirth"] = match.group(1)
        
        match = re.search(r'Gender\s*:\s*(\w+)', page_text)
        if match:
            vehicle["driver"]["gender"] = match.group(1)
        
        match = re.search(r'Marital Status\s*:\s*(\w+)', page_text)
        if match:
            vehicle["driver"]["maritalStatus"] = match.group(1)
        
        match = re.search(r'License Type\s*:\s*(\w+)', page_text)
        if match:
            vehicle["driver"]["licenseType"] = match.group(1)
        
        match = re.search(r'Licence issued\s*:\s*(\d+)', page_text)
        if match:
            vehicle["driver"]["licenseIssued"] = match.group(1)
        
        # Get total premium from this page
        match = re.search(r'TOTAL\s+([\d,.]+)', page_text)
        if match:
            vehicle["totalPremium"] = self._clean_amount(match.group(1))
        
        return vehicle["driver"]["name"] is not None
    
    def _parse_single_vehicle(self, page_text: str, page_num: int) -> Dict:
        """Parse a single motor vehicle from page text"""
        vehicle = {
            "itemReference": None,
            "riskAddress": None,
            "startDate": None,
            "make": None,
            "model": None,
            "yearOfManufacture": None,
            "vehicleSourceCode": None,
            "registration": None,
            "vinNumber": None,
            "engineNumber": None,
            "mileageRange": None,
            "vehicleCondition": None,
            "baseRetailValue": None,
            "finalSumInsured": None,
            "finalSumInsuredWithAccessories": None,
            "premium": None,
            "coverDetails": {
                "basisOfSettlement": None,
                "coverOption": None,
                "conditionOfUse": None,
                "thirdPartyLiability": None,
                "sasriaIncluded": False,
                "sasriaPremium": None
            },
            "excess": {
                "basic": None,
                "additional": None,
                "voluntary": None
            },
            "registeredOwner": {
                "name": None,
                "dateOfBirth": None
            },
            "security": {
                "firstTrackingDevice": None,
                "secondTrackingDevice": None,
                "immobiliserRequired": None,
                "overnightParking": None
            },
            "driver": {
                "name": None,
                "dateOfBirth": None,
                "gender": None,
                "maritalStatus": None,
                "licenseType": None,
                "licenseIssued": None
            },
            "totalPremium": None
        }
        
        # Item reference
        match = re.search(r'Item Reference\s*:\s*(\w+)', page_text)
        if match:
            vehicle["itemReference"] = match.group(1)
        
        # Risk address
        match = re.search(r'RISK ADDRESS\s*:\s*([^\n]+(?:\n[^\n]+)*?)(?:\nRISK DETAILS)', page_text, re.DOTALL)
        if match:
            vehicle["riskAddress"] = match.group(1).replace('\n', ', ').strip()
        
        # Start date and premium from header
        match = re.search(r'Start date\s*:\s*(\d{1,2}\s+\w+\s+\d{4})\s+([\d,.]+)', page_text)
        if match:
            vehicle["startDate"] = match.group(1)
            vehicle["premium"] = self._clean_amount(match.group(2))
        
        # Make
        match = re.search(r'Make\s*:\s*([^\n]+)', page_text)
        if match:
            vehicle["make"] = match.group(1).strip()
        
        # Model - may span multiple lines, look for the model pattern
        match = re.search(r'Model\s*:\s*([^\n]+(?:\n[^\n]+)?)', page_text)
        if match:
            model_text = match.group(1).strip()
            # Clean up model name - join lines if needed and remove extra whitespace
            # Look for year range pattern which typically ends the model
            model_match = re.search(r'^(.+?\(\d{4}\s*-\s*(?:\d{1,2}/)?(?:\d{4})?\))', model_text, re.DOTALL)
            if model_match:
                vehicle["model"] = ' '.join(model_match.group(1).split())
            else:
                vehicle["model"] = ' '.join(model_text.split()[:10])  # Take first 10 words max
        
        # Year of manufacture
        match = re.search(r'Year of manufacture\s*:\s*(\d{4})', page_text)
        if match:
            vehicle["yearOfManufacture"] = int(match.group(1))
        
        # Vehicle source code
        match = re.search(r'Vehicle source code\s*:\s*(\d+)', page_text)
        if match:
            vehicle["vehicleSourceCode"] = match.group(1)
        
        # Registration number
        match = re.search(r'Registration number\s*:\s*([A-Z0-9]+)', page_text)
        if match:
            vehicle["registration"] = match.group(1)
        
        # VIN/Chassis number
        match = re.search(r'VIN/Chassis number\s*:\s*([A-Z0-9]+)', page_text)
        if match:
            vehicle["vinNumber"] = match.group(1)
        
        # Engine number
        match = re.search(r'Engine number\s*:\s*([A-Z0-9]+)', page_text)
        if match:
            vehicle["engineNumber"] = match.group(1)
        
        # Mileage range
        match = re.search(r'Mileage range\s*:\s*(\w+)', page_text)
        if match:
            vehicle["mileageRange"] = match.group(1)
        
        # Vehicle condition
        match = re.search(r'Vehicle condition\s*:\s*(\w+)', page_text)
        if match:
            vehicle["vehicleCondition"] = match.group(1)
        
        # Base Retail Value
        match = re.search(r'Base Retail Value\s*:\s*([\d\s,]+)', page_text)
        if match:
            vehicle["baseRetailValue"] = self._clean_amount(match.group(1))
        
        # Final Sum Insured
        match = re.search(r'Final Sum Insured\s*:\s*([\d\s,]+)', page_text)
        if match:
            vehicle["finalSumInsured"] = self._clean_amount(match.group(1))
        
        # Final Sum Insured Including Accessories - handle multi-line label
        match = re.search(r'Final Sum Insured Including.*?(?:Accessories|:)\s*([\d\s,]+)', page_text, re.DOTALL)
        if match:
            vehicle["finalSumInsuredWithAccessories"] = self._clean_amount(match.group(1))
        
        # Cover details
        match = re.search(r'Basis of settlement\s*:\s*([^\n]+)', page_text)
        if match:
            vehicle["coverDetails"]["basisOfSettlement"] = match.group(1).strip()
        
        match = re.search(r'Cover option\s*:\s*(\w+)', page_text)
        if match:
            vehicle["coverDetails"]["coverOption"] = match.group(1)
        
        match = re.search(r'Condition of use\s*:\s*([^\n]+)', page_text)
        if match:
            vehicle["coverDetails"]["conditionOfUse"] = match.group(1).strip()
        
        match = re.search(r'Liability to third parties\s*:\s*([\d\s,]+)', page_text)
        if match:
            vehicle["coverDetails"]["thirdPartyLiability"] = self._clean_amount(match.group(1))
        
        # SASRIA
        if re.search(r'Sasria included\s*:\s*Yes', page_text, re.IGNORECASE):
            vehicle["coverDetails"]["sasriaIncluded"] = True
            match = re.search(r'Sasria included\s*:\s*Yes\s+([\d,.]+)', page_text)
            if match:
                vehicle["coverDetails"]["sasriaPremium"] = self._clean_amount(match.group(1))
        
        # Excess
        match = re.search(r'Basic excess\s*:\s*R\s*([\d\s,]+)', page_text)
        if match:
            vehicle["excess"]["basic"] = self._clean_amount(match.group(1))
        
        match = re.search(r'Additional excess\s*:\s*(\d+)', page_text)
        if match:
            vehicle["excess"]["additional"] = int(match.group(1))
        
        match = re.search(r'Voluntary excess\s*:\s*R\s*([\d\s,]+)', page_text)
        if match:
            vehicle["excess"]["voluntary"] = self._clean_amount(match.group(1))
        
        # Registered owner
        match = re.search(r'Registered owner\s*:\s*([^\n]+)', page_text)
        if match:
            vehicle["registeredOwner"]["name"] = match.group(1).strip()
        
        match = re.search(r"Registered owner's date of birth\s*:\s*([^\n]+)", page_text)
        if match:
            vehicle["registeredOwner"]["dateOfBirth"] = match.group(1).strip()
        
        # Security
        match = re.search(r'First tracking device type\s*:\s*(\w+)', page_text)
        if match:
            vehicle["security"]["firstTrackingDevice"] = match.group(1)
        
        match = re.search(r'Immobiliser required\s*:\s*([^\n]+)', page_text)
        if match:
            vehicle["security"]["immobiliserRequired"] = match.group(1).strip()
        
        match = re.search(r'Overnight parking\s*:\s*([^\n]+)', page_text)
        if match:
            vehicle["security"]["overnightParking"] = match.group(1).strip()
        
        # Total premium
        match = re.search(r'TOTAL\s+([\d,.]+)', page_text)
        if match:
            vehicle["totalPremium"] = self._clean_amount(match.group(1))
        
        return vehicle
    

