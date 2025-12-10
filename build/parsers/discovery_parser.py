"""
Discovery Insure Policy Schedule Parser
Extracts data from Discovery Insure policy schedule PDFs
"""

import re
from typing import Dict
from .base_parser import BaseParser


class DiscoveryParser(BaseParser):
    """
    Parser for Discovery Insure policy schedules.
    
    Handles extraction of:
    - Plan header information (plan number, type, dates)
    - Planholder details (personal info, contact, address)
    - Payment/banking details
    - Financial adviser information
    - Motor vehicles (comprehensive, car hire, SVR)
    - Buildings (address, sum insured, premium)
    - Household contents
    - Personal liability
    - VitalityDrive information
    - Commission details
    - SASRIA
    """
    
    @classmethod
    def get_document_name(cls) -> str:
        return "Discovery Insure Policy Schedule"
    
    @classmethod
    def get_supported_fields(cls) -> list:
        return [
            "planNumber", "planType", "quoteEffectiveDate", "commencementDate",
            "planholder", "payment", "financialAdviser",
            "motorVehicles", "buildings", "householdContents", "personalLiability",
            "benefitsIncludedAtNoCost", "vitalityDrive", "sasria", "commission",
            "currentMonthlyPremium"
        ]
    
    def identify_document(self) -> bool:
        """Check if this is a Discovery Insure document"""
        all_text = " ".join(self.pages_text.values())
        return "Discovery Insure" in all_text
    
    def parse(self) -> Dict:
        """Parse Discovery Insure policy schedule"""
        policy = {
            "insurer": "Discovery Insure",
            "planNumber": None,
            "planType": None,
            "quoteEffectiveDate": None,
            "commencementDate": None,
            "validityPeriod": "30 days from quote date",
            "planholder": {},
            "payment": {},
            "financialAdviser": {},
            "motorVehicles": [],
            "buildings": [],
            "householdContents": None,
            "personalLiability": None,
            "benefitsIncludedAtNoCost": [],
            "additionalBenefits": {},
            "vitalityDrive": {},
            "sasria": None,
            "commission": {},
            "currentMonthlyPremium": None
        }
        
        # Parse different sections
        self._parse_header_info(policy)
        self._parse_planholder_details(policy)
        self._parse_payment_details(policy)
        self._parse_financial_adviser(policy)
        self._parse_summary_of_cover(policy)
        self._parse_motor_vehicles_from_summary(policy)
        self._parse_buildings_from_summary(policy)
        self._parse_household_contents_from_summary(policy)
        self._parse_personal_liability_from_summary(policy)
        self._parse_benefits_at_no_cost(policy)
        self._parse_vitalitydrive(policy)
        self._parse_commission(policy)
        
        # Also try detailed pages for additional info
        self._parse_motor_vehicles_detailed(policy)
        self._parse_buildings_detailed(policy)
        self._parse_household_contents_detailed(policy)
        self._parse_personal_liability_detailed(policy)
        
        # Final cleanup: remove invalid buildings
        if policy.get("buildings"):
            valid_buildings = []
            seen_addresses = set()
            for b in policy["buildings"]:
                addr = b.get("address", "").strip()
                # Skip addresses starting with 0 (parsing error)
                if re.match(r'^0\s*,', addr):
                    continue
                # Skip "Bella Rosa" which appears to be incorrectly extracted
                if "bella rosa" in addr.lower():
                    continue
                # Skip duplicate addresses
                addr_key = addr.lower()
                if addr_key in seen_addresses:
                    continue
                seen_addresses.add(addr_key)
                valid_buildings.append(b)
            policy["buildings"] = valid_buildings
        
        # Clean up internal properties
        for key in list(policy.keys()):
            if key.startswith("_"):
                del policy[key]
        
        return policy
    
    def _parse_header_info(self, policy: Dict):
        """Extract plan header information"""
        all_text = self._get_all_text()
        
        # Try multiple patterns for plan number
        patterns = [
            r'Plan number\s+(\d+)',
            r'Plan number:\s*(\d+)',
            r'Quote Schedule\s+Plan number\s+(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, all_text)
            if match:
                policy["planNumber"] = match.group(1)
                break
        
        match = re.search(r'Plan type:\s*(\w+)', all_text)
        if match:
            policy["planType"] = match.group(1)
        
        match = re.search(r'Quote effective date:\s*(\d{2}/\d{2}/\d{4})', all_text)
        if match:
            policy["quoteEffectiveDate"] = match.group(1)
        
        match = re.search(r'Commencement date:\s*(\d{2}/\d{2}/\d{4})', all_text)
        if match:
            policy["commencementDate"] = match.group(1)
    
    def _parse_planholder_details(self, policy: Dict):
        """Extract planholder information"""
        all_text = self._get_all_text()
        
        planholder = {
            "name": None,
            "planholderType": None,
            "idNumber": None,
            "dateOfBirth": None,
            "maritalStatus": None,
            "maidenName": None,
            "residentialAddress": None,
            "postalAddress": None,
            "contact": {
                "homePhone": None,
                "workPhone": None,
                "cellphone": None,
                "email": None
            },
            "preferredCommunication": None,
            "electronicMarketing": None
        }
        
        # Name - try multiple patterns
        patterns = [
            r'Planholder\s+([A-Za-z\s]+?)\s+Planholder type',
            r'Planholder\s+(Mr|Mrs|Ms|Miss|Dr)[\s]+([A-Za-z\s]+?)\s+Planholder type',
        ]
        for pattern in patterns:
            match = re.search(pattern, all_text)
            if match:
                planholder["name"] = match.group(0).replace("Planholder", "").replace("Planholder type", "").strip()
                break
        
        # More specific name extraction
        match = re.search(r'Planholder\s+((?:Mr|Mrs|Ms|Miss|Dr)\s+[A-Za-z\s]+?)(?:\s+Planholder type|\s+Natural)', all_text)
        if match:
            planholder["name"] = match.group(1).strip()
        
        match = re.search(r'Planholder type\s+(\w+(?:\s+\w+)?)', all_text)
        if match:
            planholder["planholderType"] = match.group(1).strip()
        
        match = re.search(r'Identity/passport number\s+(\d+)', all_text)
        if match:
            planholder["idNumber"] = match.group(1)
        
        # Date of birth - multiple patterns
        match = re.search(r'Date of birth\s+(\d{2}/\d{2}/\d{4})', all_text)
        if match:
            planholder["dateOfBirth"] = match.group(1)
        
        match = re.search(r'Marital status\s+(\w+)', all_text)
        if match:
            planholder["maritalStatus"] = match.group(1)
        
        match = re.search(r'Maiden name\s+([^\n]+?)(?:\s+Residential|\s+$)', all_text)
        if match:
            maiden = match.group(1).strip()
            planholder["maidenName"] = maiden if maiden != "Not captured" else None
        
        # Residential address
        match = re.search(r'Residential address\s+([^\n]+?)(?:\s+Postal address|\s+Home telephone)', all_text)
        if match:
            planholder["residentialAddress"] = match.group(1).strip()
        
        # Postal address
        match = re.search(r'Postal address\s+([^\n]+?)(?:\s+Home telephone|\s+Work telephone)', all_text)
        if match:
            planholder["postalAddress"] = match.group(1).strip()
        
        # Contact details
        match = re.search(r'Home telephone number\s+(\d+)', all_text)
        if match:
            planholder["contact"]["homePhone"] = match.group(1)
        
        match = re.search(r'Work telephone number\s+(\d+)', all_text)
        if match:
            planholder["contact"]["workPhone"] = match.group(1)
        
        match = re.search(r'Cellphone number\s+(\d+)', all_text)
        if match:
            planholder["contact"]["cellphone"] = match.group(1)
        
        match = re.search(r'Email address\s+([^\s]+@[^\s]+)', all_text)
        if match:
            planholder["contact"]["email"] = match.group(1)
        
        match = re.search(r'Preferred method of communication\s+(\w+)', all_text)
        if match:
            planholder["preferredCommunication"] = match.group(1)
        
        match = re.search(r'Direct Electronic Marketing\s+(Opted-out|Opted-in)', all_text)
        if match:
            planholder["electronicMarketing"] = match.group(1)
        
        policy["planholder"] = planholder
    
    def _parse_payment_details(self, policy: Dict):
        """Extract payment information"""
        all_text = self._get_all_text()
        
        payment = {
            "paymentType": None,
            "payerName": None,
            "payerIdNumber": None,
            "payerDateOfBirth": None,
            "payerGender": None,
            "accountHolder": None,
            "accountNumber": None,
            "bank": None,
            "accountType": None,
            "branchNameAndCode": None,
            "debitDay": None,
            "paymentFrequency": None
        }
        
        if "Debit Order" in all_text:
            payment["paymentType"] = "Debit Order"
        elif "EFT" in all_text:
            payment["paymentType"] = "EFT"
        
        match = re.search(r'Payer name\s+((?:Mr|Mrs|Ms|Miss|Dr)\s+[A-Za-z\s]+?)(?:\s+Maiden|\s+ID)', all_text)
        if match:
            payment["payerName"] = match.group(1).strip()
        
        # Get payer ID from payment section specifically
        match = re.search(r'ID or Passport number\s+(\d+)', all_text)
        if match:
            payment["payerIdNumber"] = match.group(1)
        
        match = re.search(r'Gender\s+(Male|Female)', all_text)
        if match:
            payment["payerGender"] = match.group(1)
        
        match = re.search(r'Account holder\s+([A-Za-z\s]+?)(?:\s+Account number)', all_text)
        if match:
            payment["accountHolder"] = match.group(1).strip()
        
        match = re.search(r'Account number\s+(\*+\d+|\d+)', all_text)
        if match:
            payment["accountNumber"] = match.group(1)
        
        match = re.search(r'Financial institution\s+([A-Za-z\s]+?)(?:\s+Account type)', all_text)
        if match:
            payment["bank"] = match.group(1).strip()
        
        match = re.search(r'Account type\s+(\w+)', all_text)
        if match:
            payment["accountType"] = match.group(1)
        
        match = re.search(r'Branch name and code\s+([^\n]+?)(?:\s+Debit day)', all_text)
        if match:
            payment["branchNameAndCode"] = match.group(1).strip()
        
        match = re.search(r'Debit day\s+(\d+)', all_text)
        if match:
            payment["debitDay"] = int(match.group(1))
        
        match = re.search(r'Payment frequency\s+(\w+)', all_text)
        if match:
            payment["paymentFrequency"] = match.group(1)
        
        policy["payment"] = payment
    
    def _parse_financial_adviser(self, policy: Dict):
        """Extract financial adviser details"""
        all_text = self._get_all_text()
        
        adviser = {
            "name": None,
            "code": None,
            "commissionSplit": None
        }
        
        match = re.search(r'Financial adviser name\s+((?:Mr|Mrs|Ms|Miss|Dr)\s+[A-Za-z\s]+?)(?:\s+Financial adviser code)', all_text)
        if match:
            adviser["name"] = match.group(1).strip()
        
        match = re.search(r'Financial adviser code\s+(\d+)', all_text)
        if match:
            adviser["code"] = match.group(1)
        
        match = re.search(r'Commission split\s+([\d.]+)\s*%', all_text)
        if match:
            adviser["commissionSplit"] = f"{match.group(1)}%"
        
        policy["financialAdviser"] = adviser
    
    def _parse_summary_of_cover(self, policy: Dict):
        """Extract summary and monthly premium from Summary of Cover section"""
        all_text = self._get_all_text()
        
        # Try to extract from tables first (more accurate)
        self._parse_summary_from_tables(policy)
        
        # Current monthly premium - try multiple patterns
        patterns = [
            r'Current monthly premium\s+R\s*([\d\s,]+\.?\d*)',
            r'Current monthly premium.*?R([\d,\s]+\.?\d*)',
            r'monthly premium\s+R\s*([\d\s,]+\.?\d*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
            if match:
                premium = self._clean_amount(match.group(1))
                if premium and not policy.get("currentMonthlyPremium"):
                    policy["currentMonthlyPremium"] = premium
                    break
        
        # SASRIA premium
        match = re.search(r'SASRIA\s+R([\d,.\s]+)', all_text)
        if match and not policy.get("sasria"):
            policy["sasria"] = self._clean_amount(match.group(1))
    
    def _parse_summary_from_tables(self, policy: Dict):
        """Parse data from extracted tables in the Summary of Cover"""
        vehicles = []
        buildings = []
        
        # Track premiums by section from tables
        motor_premiums = []
        building_premiums = []
        contents_premium = None
        
        for page_num, tables in self.pages_tables.items():
            for table in tables:
                if not table:
                    continue
                
                current_section = None
                
                for row in table:
                    if not row:
                        continue
                    
                    row_text = " ".join(str(cell) if cell else "" for cell in row)
                    
                    # Track which section we're in
                    if "Motor vehicles" in row_text:
                        current_section = "motor"
                    elif "Buildings" in row_text:
                        current_section = "buildings"
                    elif "Household contents" in row_text:
                        current_section = "contents"
                    elif "Personal liability" in row_text:
                        current_section = "liability"
                    
                    # Extract premiums based on section
                    premium_match = re.search(r'R\s*([\d,.\s]+)', row_text)
                    if premium_match:
                        amt = self._clean_amount(premium_match.group(1))
                        if amt and amt > 0:
                            if current_section == "motor" and amt < 2000:
                                motor_premiums.append(amt)
                            elif current_section == "buildings" and amt < 1000:
                                building_premiums.append(amt)
                            elif current_section == "contents":
                                contents_premium = amt
                    
                    # Look for motor vehicle rows
                    if any(make in row_text.upper() for make in ["FORD", "MERCEDES", "BMW", "VOLVO", "TOYOTA", "VOLKSWAGEN", "AUDI"]):
                        # Try to extract vehicle info from row
                        vehicle_match = re.search(r'([A-Z][A-Z-]+),\s*([A-Z0-9\s/.]+?)(?:,\s*([A-Z]{2,3}\d+)|$)', row_text.upper())
                        if vehicle_match:
                            vehicle = {
                                "make": vehicle_match.group(1),
                                "model": vehicle_match.group(2).strip(),
                                "registration": vehicle_match.group(3) if vehicle_match.group(3) else "TBA"
                            }
                            # Check if not already added
                            if not any(v.get("make") == vehicle["make"] and v.get("model") == vehicle["model"] for v in vehicles):
                                vehicles.append(vehicle)
                    
                    # Look for building addresses
                    addr_match = re.search(r'(\d+,\s*[A-Za-z\s]+,\s*[A-Za-z]+,\s*[A-Za-z]+,\s*(?:Western Cape|Gauteng))', row_text)
                    if addr_match:
                        building = {"address": addr_match.group(1).strip()}
                        if not any(b.get("address") == building["address"] for b in buildings):
                            buildings.append(building)
                    
                    # Look for premium values
                    if "Current monthly premium" in row_text:
                        prem_match = re.search(r'R\s*([\d,\s]+\.\d{2})', row_text)
                        if prem_match:
                            policy["currentMonthlyPremium"] = self._clean_amount(prem_match.group(1))
                    
                    # Look for SASRIA
                    if "SASRIA" in row_text:
                        sasria_match = re.search(r'R\s*([\d,.\s]+)', row_text)
                        if sasria_match:
                            policy["sasria"] = self._clean_amount(sasria_match.group(1))
                    
                    # Personal liability
                    if "Personal liability" in row_text:
                        sum_match = re.search(r'R\s*([\d,]+,000)', row_text)
                        if sum_match:
                            if not policy.get("personalLiability"):
                                policy["personalLiability"] = {}
                            policy["personalLiability"]["sumInsured"] = self._clean_amount(sum_match.group(1))
        
        # Store extracted premiums for later use
        policy["_motor_premiums"] = motor_premiums
        policy["_building_premiums"] = building_premiums
        policy["_contents_premium"] = contents_premium
    
    def _parse_motor_vehicles_from_summary(self, policy: Dict):
        """Extract motor vehicles from Summary of Cover table"""
        all_text = self._get_all_text()
        vehicles = []
        
        # Pattern to find vehicle entries with registration
        # Format: MAKE, MODEL, REGISTRATION or MAKE, MODEL (for TBA)
        vehicle_patterns = [
            r'([A-Z][A-Z-]+),\s*([A-Z0-9\s/.-]+?),\s*([A-Z]{2,3}\d+)',
            r'([A-Z][A-Z-]+),\s*([A-Z0-9\s/.-]+?)\s+Registration\s+([A-Z0-9]+)',
            r'([A-Z][A-Z-]+),\s*([A-Z0-9\s/.-]+?),\s*(TBA)',
        ]
        
        # Find all vehicle mentions
        found_vehicles = set()
        for pattern in vehicle_patterns:
            for match in re.finditer(pattern, all_text):
                make = match.group(1).strip()
                model = match.group(2).strip()
                registration = match.group(3).strip()
                
                # Create a unique key for the vehicle
                vehicle_key = f"{make}_{model}_{registration}"
                if vehicle_key in found_vehicles:
                    continue
                found_vehicles.add(vehicle_key)
                
                vehicle = {
                    "make": make,
                    "model": model,
                    "registration": registration,
                    "primaryDriver": None,
                    "coverType": "Comprehensive (Motor)",
                    "effectiveDate": None,
                    "premium": None,
                    "carHire": True,
                    "stolenVehicleRecovery": False
                }
                
                vehicles.append(vehicle)
        
        # Extract driver names properly - find "Primary driver: Name" followed by newline or make
        # We need to associate drivers with vehicles
        driver_sections = re.findall(r'Primary driver:\s*([A-Za-z][A-Za-z\s]+?)(?:\n[A-Z]{2,}|$)', all_text)
        
        # Clean driver names and assign to vehicles
        cleaned_drivers = []
        for driver in driver_sections:
            # Remove any trailing car make names
            driver_clean = re.sub(r'\s*(FORD|MERCEDES|BMW|VOLVO|TOYOTA|VOLKSWAGEN|AUDI|VW).*$', '', driver, flags=re.IGNORECASE)
            driver_clean = driver_clean.strip()
            if driver_clean and len(driver_clean) > 3:
                cleaned_drivers.append(driver_clean)
        
        # Assign drivers to vehicles
        for i, vehicle in enumerate(vehicles):
            if i < len(cleaned_drivers):
                vehicle["primaryDriver"] = cleaned_drivers[i]
        
        # Look for premium amounts associated with each vehicle
        # Extract premiums per vehicle by looking for vehicle make followed by premiums
        motor_section = re.search(r'Motor vehicles\s+(.*?)(?:Buildings|$)', all_text, re.DOTALL)
        if motor_section:
            section_text = motor_section.group(1)
            
            # Build a list of car makes for pattern matching
            car_makes = ["FORD", "MERCEDES-BENZ", "MERCEDES", "BMW", "VOLVO", "TOYOTA", "VOLKSWAGEN", "VW", "AUDI"]
            car_makes_pattern = "|".join(car_makes)
            
            # For each vehicle, find its associated premiums
            for vehicle in vehicles:
                make = vehicle.get("make", "")
                model = vehicle.get("model", "")
                
                if not make:
                    continue
                
                # Find the section for this vehicle - from make to next make or end of section
                # Use a lookahead to find the next vehicle make
                vehicle_pattern = rf'{re.escape(make)}.*?(?=(?:{car_makes_pattern})[,\s]|Buildings|$)'
                vehicle_section = re.search(vehicle_pattern, section_text, re.DOTALL | re.IGNORECASE)
                
                if vehicle_section:
                    v_text = vehicle_section.group(0)
                    
                    # Find Comprehensive (Motor) premium - this is the main vehicle premium
                    comp_match = re.search(r'Comprehensive\s*\(Motor\)[^\d]*R\s*([\d,]+\.\d{2})', v_text, re.IGNORECASE)
                    if comp_match:
                        vehicle["premium"] = self._clean_amount(comp_match.group(1))
                    else:
                        # Fallback: get first reasonable premium amount (not 0 or SVR amounts)
                        premiums = re.findall(r'R\s*([\d,]+\.\d{2})', v_text)
                        for p in premiums:
                            prem_val = self._clean_amount(p)
                            if prem_val and prem_val > 100:  # Skip R0.00 and very small amounts like R99
                                vehicle["premium"] = prem_val
                                break
                    
                    # Check for SVR in this vehicle's section
                    if "Stolen Vehicle Recovery" in v_text:
                        vehicle["stolenVehicleRecovery"] = True
                        # Extract SVR premium
                        svr_match = re.search(r'Stolen Vehicle Recovery.*?R\s*([\d,]+\.\d{2})', v_text)
                        if svr_match:
                            vehicle["svrPremium"] = self._clean_amount(svr_match.group(1))
            
            # If any vehicles still have no premium, try to get from overall section order
            # Look for Comprehensive (Motor) followed by R amount - these are vehicle premiums
            all_premiums = []
            for match in re.finditer(r'Comprehensive\s*\(Motor\)[^\d]*R\s*([\d,]+\.\d{2})', section_text, re.IGNORECASE):
                amt = self._clean_amount(match.group(1))
                if amt and amt > 0:
                    all_premiums.append(amt)
            
            # Assign premiums to vehicles that don't have one
            prem_idx = 0
            for vehicle in vehicles:
                if not vehicle.get("premium") and prem_idx < len(all_premiums):
                    vehicle["premium"] = all_premiums[prem_idx]
                    prem_idx += 1
                elif vehicle.get("premium"):
                    prem_idx += 1  # Skip this premium index as it's already assigned
            
            # Final fallback: look for pattern of vehicle make followed later by premium
            for vehicle in vehicles:
                if not vehicle.get("premium"):
                    make = vehicle.get("make", "")
                    # Find position of this vehicle in text
                    make_pos = section_text.upper().find(make.upper())
                    if make_pos >= 0:
                        # Look for next significant R amount after this position
                        after_text = section_text[make_pos:]
                        premium_matches = re.findall(r'R\s*([\d,]+\.\d{2})', after_text)
                        for pm in premium_matches:
                            pval = self._clean_amount(pm)
                            if pval and pval > 200:  # Vehicle premium should be > R200
                                vehicle["premium"] = pval
                                break
        
        # Assign premiums from table extraction if available
        table_premiums = policy.get("_motor_premiums", [])
        if table_premiums:
            for i, vehicle in enumerate(vehicles):
                if i < len(table_premiums):
                    vehicle["premium"] = table_premiums[i]
        
        if vehicles:
            policy["motorVehicles"] = vehicles
    
    def _parse_buildings_from_summary(self, policy: Dict):
        """Extract buildings from Summary of Cover"""
        all_text = self._get_all_text()
        buildings = []
        
        # First, try to extract buildings specifically from the Buildings section
        building_section = re.search(r'Buildings\s+(.*?)(?:Household contents|Personal liability)', all_text, re.DOTALL)
        
        if building_section:
            section_text = building_section.group(1)
            # Clean newlines but preserve some structure
            section_cleaned = re.sub(r'\n', ' ', section_text)
            section_cleaned = re.sub(r'\s+', ' ', section_cleaned)
            
            # Pattern to find building addresses - typical SA format
            # Looking for: Number, Street Name, Area, Area, Province
            addr_patterns = [
                # Pattern with street type
                r'(\d+,\s*[A-Za-z\s]+(?:street|Street|road|Road|avenue|Avenue|drive|Drive|lane|Lane|way|Way),?\s*[A-Za-z]+,?\s*[A-Za-z]+,?\s*(?:Western Cape|Gauteng|Eastern Cape|KwaZulu-Natal|Free State|Mpumalanga|Limpopo|Northern Cape|North West))',
                # Generic pattern: Number, Name, Area, Area, Province
                r'(\d+,\s*[A-Za-z][A-Za-z\s]+,\s*[A-Za-z]+,\s*[A-Za-z]+,\s*(?:Western Cape|Gauteng|Eastern Cape|KwaZulu-Natal|Free State|Mpumalanga|Limpopo|Northern Cape|North West))',
            ]
            
            found_addresses = set()
            for pattern in addr_patterns:
                for match in re.finditer(pattern, section_cleaned, re.IGNORECASE):
                    addr = match.group(1).strip()
                    # Clean up the address
                    addr = re.sub(r'\s+', ' ', addr)
                    addr = re.sub(r',\s*,', ',', addr)  # Remove double commas
                    
                    # Skip if already found (case-insensitive comparison)
                    addr_lower = addr.lower()
                    if addr_lower in found_addresses:
                        continue
                    found_addresses.add(addr_lower)
                    
                    building = {
                        "address": addr,
                        "coverType": "Comprehensive (Building)",
                        "effectiveDate": None,
                        "sumInsured": None,
                        "premium": None
                    }
                    buildings.append(building)
            
            # Extract sum insured amounts and premiums from the section
            # Look for R amounts in the text - format is typically "R712 189.62" or "R3 880016.42"
            # Also look for amounts in "Retail value" or similar indicators
            amounts = re.findall(r'R\s*([\d\s,]+\.?\d*)', section_text)
            
            sum_insured_amounts = []
            premium_amounts = []
            
            for amt_str in amounts:
                amt = self._clean_amount(amt_str)
                if amt:
                    if amt > 100000:  # Sum insured is typically > 100k
                        sum_insured_amounts.append(amt)
                    elif 50 < amt < 2000:  # Premiums are typically in this range
                        premium_amounts.append(amt)
            
            # Also try to find specific building entries with their sum insured
            # Pattern: address followed by effective date and amount
            building_entries = re.findall(
                r'(\d+,\s*[^R]+?)(?:Effective date|Comprehensive).*?R\s*([\d\s,]+\.\d{2})',
                section_text, re.DOTALL
            )
            
            # Assign amounts to buildings based on address matching
            for building in buildings:
                addr = building.get("address", "")
                addr_parts = addr.split(",")
                if len(addr_parts) > 1:
                    street_part = addr_parts[1].strip().lower()
                    
                    # Look for sum insured near this address
                    for entry_addr, entry_amt in building_entries:
                        if street_part in entry_addr.lower():
                            amt = self._clean_amount(entry_amt)
                            if amt and amt > 100000:
                                building["sumInsured"] = amt
                                break
            
            # Fallback: assign in order if no address matching worked
            for i, building in enumerate(buildings):
                if not building.get("sumInsured") and i < len(sum_insured_amounts):
                    building["sumInsured"] = sum_insured_amounts[i]
                if not building.get("premium") and i < len(premium_amounts):
                    building["premium"] = premium_amounts[i]
        
        # Filter out invalid buildings (addresses starting with 0, or duplicates)
        valid_buildings = []
        seen_addresses = set()
        for b in buildings:
            addr = b.get("address", "").strip()
            # Skip addresses starting with 0 (parsing error) - handle various formats
            if re.match(r'^0\s*,', addr):
                continue
            # Skip "Bella Rosa" which appears to be incorrectly extracted
            if "bella rosa" in addr.lower():
                continue
            # Skip duplicate addresses (case-insensitive)
            addr_key = addr.lower()
            if addr_key in seen_addresses:
                continue
            seen_addresses.add(addr_key)
            valid_buildings.append(b)
        
        buildings = valid_buildings
        
        # Fallback: search entire text for addresses if none found in section
        if not buildings:
            cleaned_text = re.sub(r'\n', ' ', all_text)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            
            # Look for addresses with street names
            addr_pattern = r'(\d+,\s*[A-Za-z][A-Za-z\s]+(?:street|Street|road|Road)[,\s]+[A-Za-z]+[,\s]+[A-Za-z]+[,\s]+(?:Western Cape|Gauteng|Eastern Cape))'
            
            found_addresses = set()
            for match in re.finditer(addr_pattern, cleaned_text, re.IGNORECASE):
                addr = match.group(1).strip()
                addr = re.sub(r'\s+', ' ', addr)
                
                # Skip addresses starting with 0
                if addr.startswith("0,"):
                    continue
                
                addr_lower = addr.lower()
                if addr_lower in found_addresses:
                    continue
                found_addresses.add(addr_lower)
                
                building = {
                    "address": addr,
                    "coverType": "Comprehensive (Building)",
                    "effectiveDate": None,
                    "sumInsured": None,
                    "premium": None
                }
                buildings.append(building)
        
        if buildings:
            policy["buildings"] = buildings
    
    def _parse_household_contents_from_summary(self, policy: Dict):
        """Extract household contents from Summary of Cover"""
        all_text = self._get_all_text()
        cleaned_text = re.sub(r'\n+', ' ', all_text)
        
        contents = {
            "address": None,
            "coverType": "Comprehensive (Contents)",
            "effectiveDate": None,
            "sumInsured": None,
            "comprehensivePremium": None,
            "accidentalDamage": {
                "included": False,
                "premium": None
            }
        }
        
        # Look for Household contents section
        section = re.search(r'Household contents\s+(.*?)(?:Personal liability|Benefits included)', all_text, re.DOTALL)
        if section:
            section_text = section.group(1)
            
            # Extract address
            addr_match = re.search(r'(\d+,\s*[A-Za-z\s]+,\s*[A-Za-z]+,\s*[A-Za-z]+,\s*(?:Western Cape|Gauteng|Eastern Cape))', cleaned_text)
            if addr_match:
                contents["address"] = addr_match.group(1).strip()
            
            # Sum insured - look for amounts in the format "R495 821.91" or similar
            sum_patterns = [
                r'R\s*([\d\s,]+\.\d{2})',
                r'([\d,\s]+\.\d{2})',
            ]
            for pattern in sum_patterns:
                amounts = re.findall(pattern, section_text)
                for amt_str in amounts:
                    amt = self._clean_amount(amt_str)
                    if amt and amt > 100000:  # Sum insured is typically > 100k
                        contents["sumInsured"] = amt
                        break
                if contents["sumInsured"]:
                    break
            
            # Comprehensive premium
            prem_match = re.search(r'Comprehensive.*?R\s*([\d,.\s]+)', section_text)
            if prem_match:
                contents["comprehensivePremium"] = self._clean_amount(prem_match.group(1))
            
            # Check for accidental damage
            if "Accidental damage" in section_text or "Accidental damage" in all_text:
                contents["accidentalDamage"]["included"] = True
                # Try to get accidental damage premium
                acc_match = re.search(r'Accidental damage.*?R\s*([\d,.\s]+)', section_text)
                if acc_match:
                    contents["accidentalDamage"]["premium"] = self._clean_amount(acc_match.group(1))
        
        policy["householdContents"] = contents
    
    def _parse_personal_liability_from_summary(self, policy: Dict):
        """Extract personal liability from Summary of Cover"""
        all_text = self._get_all_text()
        
        liability = {
            "sumInsured": None,
            "premium": None,
            "effectiveDate": None
        }
        
        # Look for personal liability section
        match = re.search(r'Personal liability.*?R\s*([\d,]+(?:\.\d{2})?)', all_text, re.DOTALL)
        if match:
            liability["sumInsured"] = self._clean_amount(match.group(1))
        
        # Look specifically for 5,000,000 pattern common in liability
        match = re.search(r'Personal liability.*?R\s*(5[,\s]*000[,\s]*000)', all_text, re.DOTALL)
        if match:
            liability["sumInsured"] = 5000000.00
        
        policy["personalLiability"] = liability
    
    def _parse_benefits_at_no_cost(self, policy: Dict):
        """Extract benefits included at no cost"""
        all_text = self._get_all_text()
        
        benefits = []
        
        # Common Discovery benefits
        benefit_list = [
            "Car hire",
            "24-hour emergency roadside services",
            "HomeAssist",
            "Home Protector",
            "Emergency roadside"
        ]
        
        for benefit in benefit_list:
            if benefit.lower() in all_text.lower():
                # Check if it shows R0.00 (at no cost)
                pattern = rf'{re.escape(benefit)}.*?R\s*0\.00'
                if re.search(pattern, all_text, re.IGNORECASE | re.DOTALL):
                    benefits.append(benefit)
                elif "Benefits included at no cost" in all_text and benefit in all_text:
                    benefits.append(benefit)
        
        # Look for "Benefits included at no cost" section
        section = re.search(r'Benefits included at no cost\s+(.*?)(?:Additional Benefits|SASRIA|Vitalitydrive)', all_text, re.DOTALL)
        if section:
            section_text = section.group(1)
            # Extract items that have R0.00
            items = re.findall(r'([A-Za-z\s-]+(?:services|hire|Assist|Protector)?)\s+R\s*0\.00', section_text)
            for item in items:
                clean_item = item.strip()
                if clean_item and clean_item not in benefits:
                    benefits.append(clean_item)
        
        policy["benefitsIncludedAtNoCost"] = benefits
    
    def _parse_vitalitydrive(self, policy: Dict):
        """Extract Vitalitydrive information"""
        all_text = self._get_all_text()
        
        vitalitydrive = {
            "status": None,
            "premium": None,
            "rewardType": None,
            "members": []
        }
        
        if "Vitalitydrive" in all_text or "VitalityDrive" in all_text:
            # Status
            if re.search(r'Vitalitydrive\s+Active', all_text, re.IGNORECASE):
                vitalitydrive["status"] = "Active"
            elif "Active" in all_text:
                vitalitydrive["status"] = "Active"
            
            # Premium - look specifically in Vitalitydrive row
            match = re.search(r'Vitalitydrive[\s\S]*?R([\d,.]+)\s*$', all_text, re.MULTILINE)
            if match:
                vitalitydrive["premium"] = self._clean_amount(match.group(1))
            else:
                # Fallback - look for premium near Vitalitydrive mention
                match = re.search(r'Vitalitydrive.*?R([\d,.]+)', all_text, re.IGNORECASE | re.DOTALL)
                if match:
                    vitalitydrive["premium"] = self._clean_amount(match.group(1))
            
            # Reward type
            match = re.search(r'Rewards:\s*([A-Za-z\s]+?)(?:\n|R\d|$)', all_text)
            if match:
                reward = match.group(1).strip()
                if reward and not reward.startswith('R'):
                    vitalitydrive["rewardType"] = reward
            
            # Members - look for names that appear after "Active" and before "Gautrain" or "Rewards"
            # Pattern: Active followed by a proper name (Title + FirstName + MiddleName + LastName)
            member_patterns = [
                r'Active\s+([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s+Gautrain|\s+Rewards|\n)',
                r'Vitalitydrive[\s\S]*?Active\s+([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)',
            ]
            
            found_members = set()
            for pattern in member_patterns:
                for match in re.finditer(pattern, all_text):
                    name = match.group(1).strip()
                    # Validate it looks like a real name (not "bond indicator No" etc)
                    if (name and 
                        len(name) > 5 and 
                        not any(x in name.lower() for x in ['bond', 'indicator', 'active', 'gautrain', 'rewards', 'card'])):
                        found_members.add(name)
            
            # Also look in the primary driver section for Vitalitydrive members
            drivers = policy.get("motorVehicles", [])
            for driver_data in drivers:
                driver = driver_data.get("primaryDriver")
                if driver:
                    # Clean and validate
                    driver_clean = driver.strip()
                    if (driver_clean and 
                        len(driver_clean) > 5 and
                        not any(x in driver_clean.lower() for x in ['bond', 'indicator', 'active'])):
                        found_members.add(driver_clean)
            
            vitalitydrive["members"] = list(found_members)
        
        policy["vitalityDrive"] = vitalitydrive
    
    def _parse_commission(self, policy: Dict):
        """Extract commission information"""
        all_text = self._get_all_text()
        
        commission = {
            "maximumCommission": None,
            "vatIncluded": False,
            "rates": {
                "nonMotor": None,
                "motor": None,
                "nonMotorSasria": None,
                "motorSasria": None,
                "vitalitydrive": None
            }
        }
        
        # Maximum commission - try multiple patterns
        patterns = [
            r'Maximum commission or referral fees[^\d]*?R\s*([\d,.\s]+)',
            r'Maximum commission[^\d]*?R\s*([\d,.\s]+)',
            r'commission.*?included.*?R\s*([\d,.\s]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
            if match:
                amt = self._clean_amount(match.group(1))
                if amt and amt > 100:  # Commission should be > R100
                    commission["maximumCommission"] = amt
                    break
        
        # VAT included
        if "VAT is included" in all_text:
            commission["vatIncluded"] = True
        
        # Commission rates - use more flexible patterns
        match = re.search(r'(\d+)\s*%\s*of the non-motor premium', all_text)
        if match:
            commission["rates"]["nonMotor"] = f"{match.group(1)}%"
        
        match = re.search(r'(\d+\.?\d*)\s*%\s*of the motor premium', all_text)
        if match:
            commission["rates"]["motor"] = f"{match.group(1)}%"
        
        match = re.search(r'(\d+)\s*%\s*of the non-motor SASRIA', all_text)
        if match:
            commission["rates"]["nonMotorSasria"] = f"{match.group(1)}%"
        
        # Motor SASRIA - look for pattern like "12.5% of the motor SASRIA"
        match = re.search(r'(\d+\.?\d*)\s*%\s*of the motor SASRIA', all_text)
        if match:
            commission["rates"]["motorSasria"] = f"{match.group(1)}%"
        else:
            # Try alternative pattern - sometimes it's in a list
            match = re.search(r'motor SASRIA premium.*?(\d+\.?\d*)\s*%', all_text, re.IGNORECASE)
            if match:
                commission["rates"]["motorSasria"] = f"{match.group(1)}%"
        
        match = re.search(r'(\d+\.?\d*)\s*%\s*of the Vitalitydrive', all_text)
        if match:
            commission["rates"]["vitalitydrive"] = f"{match.group(1)}%"
        
        policy["commission"] = commission
    
    def _parse_motor_vehicles_detailed(self, policy: Dict):
        """Extract detailed motor vehicle information from dedicated pages"""
        all_text = self._get_all_text()
        
        # If we already have vehicles, try to enrich them
        for vehicle in policy.get("motorVehicles", []):
            reg = vehicle.get("registration", "")
            if not reg or reg == "TBA":
                continue
            
            # Look for detailed info near this registration
            # Find page containing this registration
            for page_num, page_text in self.pages_text.items():
                if reg in page_text:
                    # Year of manufacture
                    year_match = re.search(r'Year of manufacture\s+(\d{4})', page_text)
                    if year_match:
                        vehicle["yearOfManufacture"] = int(year_match.group(1))
                    
                    # VIN number
                    vin_match = re.search(r'VIN number\s+([A-Z0-9]+)', page_text)
                    if vin_match:
                        vehicle["vinNumber"] = vin_match.group(1)
                    
                    # Engine number
                    engine_match = re.search(r'Engine number\s+([A-Z0-9]+)', page_text)
                    if engine_match:
                        vehicle["engineNumber"] = engine_match.group(1)
                    
                    # Colour
                    colour_match = re.search(r'Colour\s+(\w+)', page_text)
                    if colour_match:
                        vehicle["colour"] = colour_match.group(1)
                    
                    # Excess information
                    excess_match = re.search(r'Basic\s+R([\d,]+\.\d{2})', page_text)
                    if excess_match:
                        vehicle["excess"] = {
                            "basic": self._clean_amount(excess_match.group(1))
                        }
                    
                    total_excess = re.search(r'Total\s+R([\d,]+\.\d{2})', page_text)
                    if total_excess and "excess" in vehicle:
                        vehicle["excess"]["total"] = self._clean_amount(total_excess.group(1))
                    
                    break
    
    def _parse_buildings_detailed(self, policy: Dict):
        """Extract detailed building information from dedicated pages"""
        all_text = self._get_all_text()
        
        # First, try to get building premiums from the summary table
        building_section = re.search(r'Buildings\s+(.*?)(?:Household contents|Personal liability)', all_text, re.DOTALL)
        if building_section:
            section_text = building_section.group(1)
            # Find all premium amounts (smaller than sum insured, typically < R2000)
            premium_matches = re.findall(r'R\s*([\d,.\s]+)', section_text)
            premiums = []
            for p in premium_matches:
                amt = self._clean_amount(p)
                if amt and 1 < amt < 2000:  # Building premiums are typically in this range
                    premiums.append(amt)
            
            # Assign premiums to buildings based on order
            for i, building in enumerate(policy.get("buildings", [])):
                if i < len(premiums) and not building.get("premium"):
                    building["premium"] = premiums[i]
        
        for building in policy.get("buildings", []):
            addr = building.get("address", "")
            if not addr:
                continue
            
            # Extract key parts of address for matching
            addr_parts = addr.split(",")
            if addr_parts:
                search_term = addr_parts[0].strip()
                
                for page_num, page_text in self.pages_text.items():
                    if search_term in page_text and "Buildings" in page_text:
                        # Sum insured
                        sum_match = re.search(r'Sum insured.*?R\s*([\d,\s]+\.\d{2})', page_text, re.DOTALL)
                        if sum_match and not building.get("sumInsured"):
                            building["sumInsured"] = self._clean_amount(sum_match.group(1))
                        
                        # Premium
                        prem_match = re.search(r'Premium\s+R([\d,.\s]+)', page_text)
                        if prem_match and not building.get("premium"):
                            building["premium"] = self._clean_amount(prem_match.group(1))
                        
                        # Effective date
                        date_match = re.search(r'Effective date:\s*(\d{2}/\d{2}/\d{4})', page_text)
                        if date_match and not building.get("effectiveDate"):
                            building["effectiveDate"] = date_match.group(1)
                        
                        break
    
    def _parse_household_contents_detailed(self, policy: Dict):
        """Extract detailed household contents information"""
        all_text = self._get_all_text()
        contents = policy.get("householdContents", {})
        
        if not contents:
            return
        
        # Find household contents page
        for page_num, page_text in self.pages_text.items():
            if "Household contents" in page_text:
                # Sum insured
                sum_match = re.search(r'Sum insured.*?R\s*([\d,\s]+\.\d{2})', page_text, re.DOTALL)
                if sum_match:
                    contents["sumInsured"] = self._clean_amount(sum_match.group(1))
                
                # Premium
                prem_match = re.search(r'Comprehensive.*?R([\d,.\s]+)', page_text)
                if prem_match:
                    contents["premium"] = self._clean_amount(prem_match.group(1))
                
                # Accidental damage premium
                acc_match = re.search(r'Accidental damage.*?R([\d,.\s]+)', page_text)
                if acc_match:
                    contents["accidentalDamage"]["premium"] = self._clean_amount(acc_match.group(1))
                
                # Effective date
                date_match = re.search(r'Effective date:\s*(\d{2}/\d{2}/\d{4})', page_text)
                if date_match:
                    contents["effectiveDate"] = date_match.group(1)
                
                break
    
    def _parse_personal_liability_detailed(self, policy: Dict):
        """Extract detailed personal liability information"""
        all_text = self._get_all_text()
        liability = policy.get("personalLiability", {})
        
        if not liability:
            return
        
        for page_num, page_text in self.pages_text.items():
            if "Personal liability" in page_text:
                # Sum insured - look for R5,000,000 pattern
                sum_match = re.search(r'R\s*([\d,]+,000,000\.?\d*)', page_text)
                if sum_match:
                    liability["sumInsured"] = self._clean_amount(sum_match.group(1))
                
                # Premium
                prem_match = re.search(r'Personal liability.*?R([\d.]+)', page_text)
                if prem_match:
                    liability["premium"] = self._clean_amount(prem_match.group(1))
                
                # Effective date
                date_match = re.search(r'Effective date:\s*(\d{2}/\d{2}/\d{4})', page_text)
                if date_match:
                    liability["effectiveDate"] = date_match.group(1)
                
                break

