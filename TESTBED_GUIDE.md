# Insurance Parser API Testbed - Setup & Testing Guide

## Overview

This guide provides complete instructions for setting up and testing the Insurance Parser API using the provided HTML testbed interface.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup Instructions](#detailed-setup-instructions)
4. [Using the Testbed](#using-the-testbed)
5. [Testing Scenarios](#testing-scenarios)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)

---

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **pip** (Python package installer)
- **Modern web browser** (Chrome, Firefox, Edge, Safari)

### Optional (for containerized deployment)
- **Docker** - [Download](https://www.docker.com/get-started)
- **Docker Compose** (included with Docker Desktop)

### Files Needed
- `insurance_parser_api.py` - The API server
- `requirements.txt` - Python dependencies
- `insurance_parser_testbed.html` - The testbed interface
- Sample PDF file(s) for testing

---

## Quick Start

### Option 1: Local Python Setup (Recommended for Testing)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the API server
python insurance_parser_api.py

# 3. Open the testbed
# Simply double-click insurance_parser_testbed.html
# or open it in your browser
```

### Option 2: Docker Setup

```bash
# 1. Build the Docker image
docker build -t insurance-parser-api .

# 2. Run the container
docker run -p 8000:8000 insurance-parser-api

# 3. Open the testbed
# Double-click insurance_parser_testbed.html
```

### Option 3: Docker Compose

```bash
# 1. Start the service
docker-compose up

# 2. Open the testbed
# Double-click insurance_parser_testbed.html
```

---

## Detailed Setup Instructions

### Step 1: Prepare Your Environment

#### Create a Project Directory
```bash
mkdir insurance-parser-project
cd insurance-parser-project
```

#### Place All Files in the Directory
```
insurance-parser-project/
├── insurance_parser_api.py
├── requirements.txt
├── insurance_parser_testbed.html
├── Dockerfile (optional)
├── docker-compose.yml (optional)
└── test-pdfs/
    └── sample_policy.pdf
```

### Step 2: Install Python Dependencies

#### Using pip (Standard)
```bash
pip install -r requirements.txt
```

#### Using pip with Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
# Check installed packages
pip list

# You should see:
# - fastapi
# - uvicorn
# - pdfplumber
# - python-multipart
# - pydantic
```

### Step 4: Start the API Server

#### Standard Method
```bash
python insurance_parser_api.py
```

#### Production Method (with uvicorn)
```bash
uvicorn insurance_parser_api:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 5: Verify API is Running

Open your browser and navigate to:
- **Health Check**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json

You should see the API documentation (Swagger UI).

### Step 6: Open the Testbed

1. Locate `insurance_parser_testbed.html`
2. Double-click to open in your default browser
3. OR right-click → Open With → Choose your browser

---

## Using the Testbed

### Interface Overview

The testbed interface has four main sections:

#### 1. API Configuration
- **API Endpoint URL**: The address of your API server (default: `http://localhost:8000`)
- **Insurer Selection**: Choose specific insurer or auto-detect
- **Test Connection**: Verify API is accessible

#### 2. Upload Section
- **Drag & Drop Area**: Drop PDF files here
- **Browse Button**: Click to select files from file system
- **File Info**: Shows selected file name and size
- **Parse Button**: Initiates parsing

#### 3. Results Display
- **Statistics Dashboard**: Shows insurer, processing time, field count
- **Structured View Tab**: Organized, human-readable format
- **Raw JSON Tab**: Plain JSON output
- **Pretty JSON Tab**: Syntax-highlighted JSON

#### 4. Action Buttons
- **Download JSON**: Save parsed data as .json file
- **Copy**: Copy JSON to clipboard
- **Parse Another**: Reset and upload new document

### Step-by-Step Usage

#### Step 1: Test API Connection
1. Ensure API is running (see Setup Step 4)
2. Click **"Test Connection"** button
3. Wait for status indicator:
   - ✅ **Connected** (green) - API is ready
   - ⚠️ **Unexpected response** (yellow) - API responding but unusual
   - ❌ **Connection failed** (red) - API not accessible

#### Step 2: Upload a PDF
Choose one of these methods:

**Method A: Drag & Drop**
1. Open your file explorer
2. Navigate to your PDF file
3. Drag the file over the upload area
4. Drop when the area highlights
5. File info will display below

**Method B: Click to Browse**
1. Click anywhere in the upload area
2. OR click the **"Browse Files"** button
3. Select your PDF file
4. Click "Open"
5. File info will display below

**Method C: Server Path (for files already on server)**
1. Scroll to "Test with Sample" section
2. Enter the server file path
3. Click **"Parse from Server Path"**

#### Step 3: Configure Insurer (Optional)
1. Select insurer from dropdown if known
2. Leave as "Auto-detect" for automatic identification
3. Supported insurers:
   - Discovery
   - Santam
   - Old Mutual
   - Outsurance

#### Step 4: Parse the Document
1. Click **"Parse Document"** button
2. Wait for processing (loading indicator appears)
3. Processing typically takes 2-5 seconds

#### Step 5: View Results

**Structured View (Default)**
- Organized sections with icons
- Easy-to-read format
- Grouped by category:
  - Policy Information
  - Planholder
  - Payment Details
  - Motor Vehicles
  - Buildings
  - Household Contents
  - Personal Liability
  - Additional Benefits

**Raw JSON View**
- Plain JSON format
- Complete data structure
- Click **"Copy"** to copy to clipboard

**Pretty JSON View**
- Color-coded syntax highlighting
- Keys in blue
- Strings in orange
- Numbers in green
- Booleans/null in blue

#### Step 6: Export Results
1. **Download JSON**: Saves as `parsed_[filename].json`
2. **Copy**: Copies JSON to clipboard for pasting elsewhere

---

## Testing Scenarios

### Test Case 1: Successful Parse - Discovery Policy

**Objective**: Verify complete parsing of Discovery Insure policy

**Steps**:
1. Start API server
2. Open testbed
3. Test connection (should be green ✅)
4. Upload: `Discovery_Insure_Plan_Schedule_-_2022_unlocked.pdf`
5. Select insurer: "Auto-detect" or "Discovery"
6. Click "Parse Document"

**Expected Results**:
- Processing completes in 2-5 seconds
- Status: Success
- Insurer detected: "Discovery"
- Statistics show:
  - Processing time: ~2-4 seconds
  - Fields extracted: 50+ fields
- Structured view displays all sections:
  - ✅ Policy Information (plan number, type, dates)
  - ✅ Planholder (name, ID, contact details)
  - ✅ Payment Details (bank, account info)
  - ✅ Motor Vehicles (description, premium, excess)
  - ✅ Buildings (address, sum insured)
  - ✅ Household Contents
  - ✅ Personal Liability
  - ✅ Additional Benefits

**Sample Expected Output**:
```json
{
  "insurer": "Discovery",
  "data": {
    "policy_number": "4000638715",
    "plan_type": "Classic",
    "monthly_premium": "R4,119.89",
    "planholder": {
      "name": "Cedric Percival Keown",
      "id_number": "6908155180084",
      "email": "cedric.keown@gmail.com"
    }
  }
}
```

---

### Test Case 2: Auto-Detection Test

**Objective**: Verify insurer auto-detection works correctly

**Steps**:
1. Upload any insurance PDF
2. Select insurer: "Auto-detect"
3. Parse document

**Expected Results**:
- Correct insurer identified
- Appropriate parser used
- Insurer name displayed in stats

---

### Test Case 3: Invalid File Handling

**Objective**: Test error handling for non-PDF files

**Steps**:
1. Attempt to upload a .txt or .docx file

**Expected Results**:
- File rejected
- Alert message: "Please select a PDF file"
- Upload area remains empty

---

### Test Case 4: Large File Processing

**Objective**: Test performance with large PDFs

**Steps**:
1. Upload PDF > 5MB
2. Monitor processing time

**Expected Results**:
- Processing completes successfully
- Time displayed in statistics
- No timeout errors

**Performance Benchmarks**:
- < 1MB: 1-2 seconds
- 1-5MB: 3-5 seconds
- 5-10MB: 5-10 seconds

---

### Test Case 5: Network Error Handling

**Objective**: Test behavior when API is offline

**Steps**:
1. Stop the API server (Ctrl+C)
2. Try to test connection
3. Try to parse a document

**Expected Results**:
- Connection test shows: ❌ "Connection failed"
- Parse attempt shows error message
- User-friendly error display

---

### Test Case 6: Multiple Document Processing

**Objective**: Test parsing multiple documents in sequence

**Steps**:
1. Parse first document
2. Click "Parse Another Document"
3. Upload second document
4. Parse second document

**Expected Results**:
- First results cleared
- Second document processes successfully
- No data from first document persists

---

### Test Case 7: Download & Copy Functions

**Objective**: Verify export functionality

**Steps**:
1. Parse a document successfully
2. Click "Download JSON"
3. Check downloaded file
4. Click "Copy" button
5. Paste into text editor

**Expected Results**:
- JSON file downloads with correct filename
- File contains complete parsed data
- Copy function places JSON on clipboard
- Pasted content matches displayed JSON

---

### Test Case 8: Server Path Parsing

**Objective**: Test parsing files already on the server

**Steps**:
1. Locate file on server (e.g., `/mnt/user-data/uploads/sample.pdf`)
2. Enter path in "Test with Sample" section
3. Click "Parse from Server Path"

**Expected Results**:
- Document parses without upload
- Results display normally
- Faster processing (no upload time)

---

## Troubleshooting

### Issue 1: "Connection Failed" Error

**Symptoms**:
- Red X icon next to connection status
- Cannot parse documents

**Solutions**:
1. **Verify API is running**:
   ```bash
   # Check if process is running
   # On Windows:
   netstat -ano | findstr :8000
   # On macOS/Linux:
   lsof -i :8000
   ```

2. **Check API endpoint URL**:
   - Should be: `http://localhost:8000`
   - Try: `http://127.0.0.1:8000`

3. **Restart the API server**:
   ```bash
   # Stop (Ctrl+C) and restart
   python insurance_parser_api.py
   ```

4. **Check firewall settings**:
   - Ensure port 8000 is not blocked
   - Temporarily disable firewall to test

5. **Verify Python environment**:
   ```bash
   # Check all dependencies installed
   pip list | grep -E "fastapi|uvicorn|pdfplumber"
   ```

---

### Issue 2: PDF Not Parsing / Timeout

**Symptoms**:
- Loading indicator stays indefinitely
- No results or error displayed

**Solutions**:
1. **Check file size**:
   - Large files (>10MB) may take longer
   - Try smaller test file first

2. **Check API logs**:
   ```bash
   # Look for errors in terminal where API is running
   # Common errors:
   # - ImportError: Module not found
   # - PermissionError: Cannot read file
   # - MemoryError: File too large
   ```

3. **Verify PDF is valid**:
   - Open PDF in Adobe Reader or browser
   - Ensure PDF is not corrupted
   - Check if PDF is password-protected

4. **Test with sample file**:
   - Use provided Discovery sample
   - If sample works, issue is with your PDF

---

### Issue 3: Incorrect Data Extracted

**Symptoms**:
- Parsing completes but data is wrong
- Missing fields or incorrect values

**Solutions**:
1. **Check insurer selection**:
   - Ensure correct insurer is selected
   - Or use "Auto-detect"

2. **Verify PDF format**:
   - Different policy versions may have different formats
   - Parser may need updates for new formats

3. **Review API logs for warnings**:
   - Check for "Pattern not matched" messages
   - May indicate format changes

4. **Report issue**:
   - Note the insurer and policy type
   - Provide sample PDF (with sensitive data removed)

---

### Issue 4: Testbed Not Loading in Browser

**Symptoms**:
- Blank page or error when opening HTML
- Console errors (press F12 to view)

**Solutions**:
1. **Check browser compatibility**:
   - Use modern browser (Chrome, Firefox, Edge, Safari)
   - Update browser to latest version

2. **Check internet connection**:
   - Testbed loads Bootstrap from CDN
   - Offline? Save CDN resources locally

3. **Disable browser extensions**:
   - Ad blockers may interfere
   - Try incognito/private mode

4. **Check JavaScript enabled**:
   - Ensure JavaScript is not blocked
   - Browser settings → Enable JavaScript

---

### Issue 5: CORS Errors (Cross-Origin)

**Symptoms**:
- Console shows: "blocked by CORS policy"
- API reachable but testbed cannot connect

**Solutions**:
1. **Enable CORS in API**:
   ```python
   # Add to insurance_parser_api.py
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # Allow all origins
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Use same protocol**:
   - If API is HTTP, testbed must use HTTP
   - If API is HTTPS, testbed must use HTTPS

3. **Run from web server**:
   ```bash
   # Instead of file://, serve via HTTP
   python -m http.server 8080
   # Open: http://localhost:8080/insurance_parser_testbed.html
   ```

---

### Issue 6: File Upload Fails

**Symptoms**:
- File selected but parsing doesn't start
- Upload area shows file but parse button disabled

**Solutions**:
1. **Check file type**:
   - Only PDF files accepted
   - Check file extension is .pdf

2. **Check file size**:
   - API may have size limit (default: 10MB)
   - Compress PDF if too large

3. **Clear browser cache**:
   - Cached JavaScript may be outdated
   - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

4. **Try different upload method**:
   - If drag-drop fails, try browse button
   - Or use server path method

---

## Advanced Configuration

### Changing API Port

If port 8000 is in use, change to another port:

```bash
# Method 1: Command line
python insurance_parser_api.py --port 8080

# Method 2: Edit insurance_parser_api.py
# Change the last line to:
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

# Then update testbed:
# Change API Endpoint to: http://localhost:8080
```

### Running on Network (Accessible from Other Devices)

1. **Find your local IP address**:
   ```bash
   # Windows:
   ipconfig
   # Look for IPv4 Address
   
   # macOS/Linux:
   ifconfig
   # or
   ip addr show
   ```

2. **Start API with network binding**:
   ```bash
   python insurance_parser_api.py
   # Already binds to 0.0.0.0
   ```

3. **Update testbed on other devices**:
   - Change API endpoint to: `http://[YOUR_IP]:8000`
   - Example: `http://192.168.1.100:8000`

4. **Check firewall**:
   - Allow incoming connections on port 8000

### Enabling HTTPS (for production)

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout key.pem -out cert.pem -days 365

# Run with SSL
uvicorn insurance_parser_api:app \
  --host 0.0.0.0 \
  --port 8443 \
  --ssl-keyfile=key.pem \
  --ssl-certfile=cert.pem

# Update testbed API endpoint to:
# https://localhost:8443
```

### Customizing Upload Size Limit

Edit `insurance_parser_api.py`:

```python
# Add near the top
MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB

# Then in parse endpoint, add:
@app.post("/parse")
async def parse_pdf(file: UploadFile = File(...)):
    # Check file size
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {MAX_UPLOAD_SIZE/(1024*1024)}MB"
        )
    # ... rest of code
```

### Adding Authentication

For production deployment, add API key authentication:

```python
# Add to insurance_parser_api.py
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY = "your-secret-api-key-here"
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key

# Add to endpoints
@app.post("/parse")
async def parse_pdf(
    file: UploadFile = File(...),
    api_key: str = Security(verify_api_key)
):
    # ... existing code
```

Then update testbed to include API key in requests.

---

## Performance Optimization Tips

### 1. Use Production Server
```bash
# Instead of development server
gunicorn insurance_parser_api:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### 2. Enable Caching
Add caching for frequently parsed documents to reduce processing time.

### 3. Increase Workers
For high traffic, increase number of workers:
```bash
uvicorn insurance_parser_api:app --workers 4
```

### 4. Use Docker for Consistency
Docker ensures consistent environment across all deployments.

---

## Testing Checklist

Before deploying to production, verify:

- [ ] API health check returns 200 OK
- [ ] Supported insurers endpoint returns list
- [ ] Discovery PDF parses successfully
- [ ] Auto-detection identifies insurer correctly
- [ ] All sections extract data properly
- [ ] JSON output is valid and complete
- [ ] Download function saves correct file
- [ ] Copy function works in all browsers
- [ ] Error messages display for invalid files
- [ ] Large files (5-10MB) process without timeout
- [ ] Multiple consecutive uploads work correctly
- [ ] Server path parsing works (if used)
- [ ] API handles concurrent requests
- [ ] Testbed responsive on mobile devices
- [ ] All browsers render testbed correctly (Chrome, Firefox, Safari, Edge)

---

## Next Steps

After successful testing:

1. **Deploy to production** - See DEPLOYMENT_GUIDE.md
2. **Add more insurers** - Implement parsers for Santam, Old Mutual, etc.
3. **Enhance error handling** - Add more specific error messages
4. **Implement authentication** - Secure API with API keys
5. **Add monitoring** - Track usage and performance
6. **Set up logging** - Store parsed results for analysis
7. **Create backups** - Backup parsed data regularly

---

## Support & Resources

### Documentation
- **API Documentation**: http://localhost:8000/docs (when running)
- **Solution Summary**: SOLUTION_SUMMARY.md
- **Deployment Guide**: DEPLOYMENT_GUIDE.md
- **Technical README**: README.md

### Troubleshooting
- Check API logs in terminal
- Review browser console (F12) for JavaScript errors
- Test API directly with curl or Postman
- Verify Python environment and dependencies

### Sample Commands for Manual Testing

```bash
# Test API health
curl http://localhost:8000/

# Test supported insurers
curl http://localhost:8000/supported-insurers

# Test parse endpoint with curl
curl -X POST "http://localhost:8000/parse" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_policy.pdf"

# Test server path parsing
curl -X POST "http://localhost:8000/parse-from-path?filepath=/path/to/file.pdf" \
  -H "accept: application/json"
```

---

## Appendix: System Requirements

### Minimum Requirements
- **CPU**: 1 core, 2.0 GHz
- **RAM**: 512 MB
- **Disk**: 100 MB free space
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8+
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

### Recommended for Production
- **CPU**: 2+ cores, 2.5 GHz
- **RAM**: 2 GB
- **Disk**: 1 GB free space
- **Network**: Stable internet connection
- **Docker**: 20.10+ (if using containers)

---

## Version History

- **v1.0.0** (2024-12-09)
  - Initial release
  - Discovery parser implemented
  - HTML testbed created
  - Basic API functionality

---

## License & Credits

**Built with**:
- FastAPI - Web framework
- pdfplumber - PDF processing
- Bootstrap 5 - UI framework
- Phoenix Theme - Bootstrap theme

**CustomApp Brand Colors**:
- Background: #5CBDB4 (Teal/Turquoise)
- Text: #4A4A4A (Charcoal Grey)

---

**End of Testing Guide**
