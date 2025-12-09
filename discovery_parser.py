#!/usr/bin/env python3
"""
Discovery Insure Policy Schedule Parser
Extracts structured data from Discovery Insure PDF documents to JSON
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import pdfplumber

class DiscoveryInsureParser:
    """Parser for Discovery Insure policy schedules"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pages_text = {}
        
    def extract_text(self):
        """Extract text from all pages"""
        with pdfplumber.open(self.pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                self.pages_text[i] = page.extract_text()
    
    def parse(self) -> Dict:
        """Parse the entire policy document"""
        self.extract_text()
        
        policy = {
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
        self.parse_header_info(policy)
        self.parse_planholder_details(policy)
        self.parse_payment_details(policy)
        self.parse_summary_of_cover(policy)
        self.parse_motor_vehicles(policy)
        self.parse_buildings(policy)
        self.parse_household_contents(policy)
        self.parse_personal_liability(policy)
        
        return policy
    
    def parse_header_info(self, policy: Dict):
        """Extract plan number, type, and dates"""
        page2 = self.pages_text.get(2, "")
        
        # Plan number
        match = re.search(r'Plan number\s+(\d+)', page2)
        if match:
            policy["planNumber"] = match.group(1)
        
        # Plan type
        match = re.search(r'Plan type:\s+(\w+)', page2)
        if match:
            policy["planType"] = match.group(1)
        
        # Quote effective date
        match = re.search(r'Quote effective date:\s+(\d{2}/\d{2}/\d{4})', page2)
        if match:
            policy["quoteEffectiveDate"] = match.group(1)
        
        # Commencement date
        match = re.search(r'Commencement date:\s+(\d{2}/\d{2}/\d{4})', page2)
        if match:
            policy["commencementDate"] = match.group(1)
    
    def parse_planholder_details(self, policy: Dict):
        """Extract planholder information"""
        page2 = self.pages_text.get(2, "")
        
        planholder = {
            "name": None,
            "idNumber": None,
            "dateOfBirth": None,
            "maritalStatus": None,
            "residentialAddress": {},
            "postalAddress": {},
            "contact": {}
        }
        
        # Name
        match = re.search(r'Planholder\s+([^\n]+?)\s+Planholder type', page2)
        if match:
            planholder["name"] = match.group(1).strip()
        
        # ID Number
        match = re.search(r'Identity/passport number\s+(\d+)', page2)
        if match:
            planholder["idNumber"] = match.group(1)
        
        # Date of birth
        match = re.search(r'Date of birth\s+(\d{2}/\d{2}/\d{4})', page2)
        if match:
            planholder["dateOfBirth"] = match.group(1)
        
        # Marital status
        match = re.search(r'Marital status\s+(\w+)', page2)
        if match:
            planholder["maritalStatus"] = match.group(1)
        
        # Email
        match = re.search(r'Email address\s+([^\s]+@[^\s]+)', page2)
        if match:
            planholder["contact"]["email"] = match.group(1)
        
        # Cellphone
        match = re.search(r'Cellphone number\s+(\d+)', page2)
        if match:
            planholder["contact"]["cellphone"] = match.group(1)
        
        # Home phone
        match = re.search(r'Home telephone number\s+(\d+)', page2)
        if match:
            planholder["contact"]["homePhone"] = match.group(1)
        
        # Work phone
        match = re.search(r'Work telephone number\s+(\d+)', page2)
        if match:
            planholder["contact"]["workPhone"] = match.group(1)
        
        # Residential address
        match = re.search(r'Residential address\s+(.+?)\s+Postal address', page2, re.DOTALL)
        if match:
            address_text = match.group(1).strip()
            planholder["residentialAddress"] = self.parse_address(address_text)
        
        policy["planholder"] = planholder
    
    def parse_address(self, address_text: str) -> Dict:
        """Parse address string into components"""
        parts = [p.strip() for p in address_text.split(',')]
        return {
            "fullAddress": address_text,
            "street": parts[0] if len(parts) > 0 else None,
            "suburb": parts[1] if len(parts) > 1 else None,
            "city": parts[2] if len(parts) > 2 else None,
            "province": parts[3] if len(parts) > 3 else None
        }
    
    def parse_payment_details(self, policy: Dict):
        """Extract payment information"""
        page3 = self.pages_text.get(3, "")
        
        payment = {
            "paymentType": None,
            "accountHolder": None,
            "bank": None,
            "accountType": None,
            "branchCode": None,
            "debitDay": None,
            "paymentFrequency": None
        }
        
        # Payment type
        if "Debit Order Payment Type Selected" in page3:
            payment["paymentType"] = "Debit Order"
        
        # Account holder
        match = re.search(r'Account holder\s+(.+?)\s+Account number', page3)
        if match:
            payment["accountHolder"] = match.group(1).strip()
        
        # Bank
        match = re.search(r'Financial institution\s+(.+?)\s+Account type', page3)
        if match:
            payment["bank"] = match.group(1).strip()
        
        # Account type
        match = re.search(r'Account type\s+(\w+)', page3)
        if match:
            payment["accountType"] = match.group(1)
        
        # Branch code
        match = re.search(r'Branch name and code\s+Branch \d+\s+(\d+)', page3)
        if match:
            payment["branchCode"] = match.group(1)
        
        # Debit day
        match = re.search(r'Debit day\s+(\d+)', page3)
        if match:
            payment["debitDay"] = int(match.group(1))
        
        # Payment frequency
        match = re.search(r'Payment frequency\s+(\w+)', page3)
        if match:
            payment["paymentFrequency"] = match.group(1)
        
        policy["payment"] = payment
    
    def parse_summary_of_cover(self, policy: Dict):
        """Extract summary information and monthly premium"""
        page4 = self.pages_text.get(4, "")
        
        # Current monthly premium
        match = re.search(r'Current monthly premium\s+R\s*([\d\s,]+\.\d{2})', page4)
        if match:
            premium_str = match.group(1).replace(' ', '').replace(',', '')
            policy["currentMonthlyPremium"] = float(premium_str)
        
        # SASRIA
        match = re.search(r'SASRIA\s+R([\d.]+)', page4)
        if match:
            policy["additionalBenefits"]["sasria"] = float(match.group(1))
        
        # Vitalitydrive
        match = re.search(r'Vitalitydrive.*?R([\d.]+)', page4)
        if match:
            policy["additionalBenefits"]["vitalitydrive"] = float(match.group(1))
    
    def parse_motor_vehicles(self, policy: Dict):
        """Extract motor vehicle information"""
        vehicles = []
        
        # Look through pages 6-11
        for page_num in range(6, 12):
            page_text = self.pages_text.get(page_num, "")
            
            # Check if this page contains a motor vehicle
            match = re.search(r'(\d+)\.\s+([A-Z-]+),\s+([A-Z0-9\s/]+?)\s+Registration\s+(\w+)', page_text)
            if match:
                vehicle = {
                    "vehicleNumber": int(match.group(1)),
                    "make": match.group(2),
                    "model": match.group(3).strip(),
                    "registration": match.group(4),
                    "primaryDriver": None,
                    "effectiveDate": None,
                    "coverType": "Comprehensive",
                    "premium": None,
                    "excess": {},
                    "details": {}
                }
                
                # Primary driver
                driver_match = re.search(r'Primary driver details:\s+(.+)', page_text)
                if driver_match:
                    vehicle["primaryDriver"] = driver_match.group(1).strip()
                
                # Premium
                premium_match = re.search(r'Total\s+R([\d,]+\.\d{2})', page_text)
                if premium_match:
                    vehicle["premium"] = float(premium_match.group(1).replace(',', ''))
                
                # Excess
                excess_match = re.search(r'Excess motor.*?Basic\s+R([\d,]+\.\d{2}).*?Voluntary\s+R([\d,]+\.\d{2}).*?Total\s+R([\d,]+\.\d{2})', page_text, re.DOTALL)
                if excess_match:
                    vehicle["excess"] = {
                        "basic": float(excess_match.group(1).replace(',', '')),
                        "voluntary": float(excess_match.group(2).replace(',', '')),
                        "total": float(excess_match.group(3).replace(',', ''))
                    }
                
                # Vehicle details
                year_match = re.search(r'Year of manufacture\s+(\d{4})', page_text)
                if year_match:
                    vehicle["details"]["yearOfManufacture"] = int(year_match.group(1))
                
                color_match = re.search(r'Colour\s+(\w+)', page_text)
                if color_match:
                    vehicle["details"]["colour"] = color_match.group(1)
                
                vin_match = re.search(r'VIN number\s+([A-Z0-9]+)', page_text)
                if vin_match:
                    vehicle["details"]["vinNumber"] = vin_match.group(1)
                
                engine_match = re.search(r'Engine number\s+([A-Z0-9]+)', page_text)
                if engine_match:
                    vehicle["details"]["engineNumber"] = engine_match.group(1)
                
                tracking_match = re.search(r'Tracking device\s+(.+)', page_text)
                if tracking_match:
                    vehicle["details"]["trackingDevice"] = tracking_match.group(1).strip()
                
                finance_match = re.search(r'Finance house:\s+(.+)', page_text)
                if finance_match:
                    vehicle["details"]["financeHouse"] = finance_match.group(1).strip()
                
                vehicles.append(vehicle)
        
        policy["motorVehicles"] = vehicles
    
    def parse_buildings(self, policy: Dict):
        """Extract building information"""
        buildings = []
        
        # Look through pages 12-15
        for page_num in range(12, 16):
            page_text = self.pages_text.get(page_num, "")
            
            # Check if this page contains a building
            if "Buildings" in page_text and re.search(r'\d+\.\s+.+\s+Registration', page_text):
                building = {
                    "address": None,
                    "effectiveDate": None,
                    "sumInsured": None,
                    "premium": None,
                    "coverType": "Comprehensive",
                    "excess": {}
                }
                
                # Address
                addr_match = re.search(r'\d+\.\s+(.+?)\s+Registration', page_text)
                if addr_match:
                    building["address"] = addr_match.group(1).strip()
                
                # Sum insured
                sum_match = re.search(r'Sum insured.*?R\s*([\d,\s]+\.\d{2})', page_text, re.DOTALL)
                if sum_match:
                    sum_str = sum_match.group(1).replace(',', '').replace(' ', '')
                    building["sumInsured"] = float(sum_str)
                
                # Premium
                prem_match = re.search(r'Premium\s+R([\d.]+)', page_text)
                if prem_match:
                    building["premium"] = float(prem_match.group(1))
                
                # Effective date
                date_match = re.search(r'Effective date:\s+(\d{2}/\d{2}/\d{4})', page_text)
                if date_match:
                    building["effectiveDate"] = date_match.group(1)
                
                # Excess
                excess_match = re.search(r'Excess building.*?Basic\s+R([\d,]+\.\d{2}).*?Total\s+R([\d,]+\.\d{2})', page_text, re.DOTALL)
                if excess_match:
                    building["excess"] = {
                        "basic": float(excess_match.group(1).replace(',', '')),
                        "total": float(excess_match.group(2).replace(',', ''))
                    }
                
                if building["address"]:
                    buildings.append(building)
        
        policy["buildings"] = buildings
    
    def parse_household_contents(self, policy: Dict):
        """Extract household contents information"""
        # Look through pages 16-17
        for page_num in range(16, 18):
            page_text = self.pages_text.get(page_num, "")
            
            if "Household contents" in page_text:
                contents = {
                    "address": None,
                    "effectiveDate": None,
                    "sumInsured": None,
                    "premium": None,
                    "excess": {}
                }
                
                # Address
                addr_match = re.search(r'Household contents\s+\d+\.\s+(.+?)\s+Plan details', page_text)
                if addr_match:
                    contents["address"] = addr_match.group(1).strip()
                
                # Sum insured
                sum_match = re.search(r'Sum insured.*?R\s*([\d,\s]+\.\d{2})', page_text, re.DOTALL)
                if sum_match:
                    sum_str = sum_match.group(1).replace(',', '').replace(' ', '')
                    contents["sumInsured"] = float(sum_str)
                
                # Premium
                prem_match = re.search(r'Total.*?R([\d,.]+)', page_text, re.DOTALL)
                if prem_match:
                    contents["premium"] = float(prem_match.group(1).replace(',', ''))
                
                # Effective date
                date_match = re.search(r'Effective date:\s+(\d{2}/\d{2}/\d{4})', page_text)
                if date_match:
                    contents["effectiveDate"] = date_match.group(1)
                
                policy["householdContents"] = contents
                break
    
    def parse_personal_liability(self, policy: Dict):
        """Extract personal liability information"""
        # Look through pages 18-19
        for page_num in range(18, 20):
            page_text = self.pages_text.get(page_num, "")
            
            if "Personal liability" in page_text:
                liability = {
                    "effectiveDate": None,
                    "sumInsured": None,
                    "premium": None
                }
                
                # Sum insured
                sum_match = re.search(r'Sum insured.*?R([\d,]+\.\d{2})', page_text, re.DOTALL)
                if sum_match:
                    liability["sumInsured"] = float(sum_match.group(1).replace(',', ''))
                
                # Premium
                prem_match = re.search(r'Premium.*?R([\d.]+)', page_text, re.DOTALL)
                if prem_match:
                    liability["premium"] = float(prem_match.group(1))
                
                # Effective date
                date_match = re.search(r'Effective date:\s+(\d{2}/\d{2}/\d{4})', page_text)
                if date_match:
                    liability["effectiveDate"] = date_match.group(1)
                
                policy["personalLiability"] = liability
                break


def main():
    """Main execution function"""
    pdf_path = "/mnt/user-data/uploads/noQId_Discovery_Insure_Plan_Schedule_-_2022_unlocked.pdf"
    
    try:
        print("Parsing Discovery Insure Policy Schedule...\n")
        
        parser = DiscoveryInsureParser(pdf_path)
        policy_data = parser.parse()
        
        # Convert to JSON
        json_output = json.dumps(policy_data, indent=2)
        print(json_output)
        
        # Save to file
        output_path = "/mnt/user-data/outputs/policy_schedule.json"
        with open(output_path, 'w') as f:
            f.write(json_output)
        
        print(f"\n\nJSON saved to: {output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
