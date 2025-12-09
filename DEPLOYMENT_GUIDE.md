# Insurance Policy Parser Web Service - Deployment Guide

## Overview

This web service provides a RESTful API for extracting structured data from insurance policy schedule PDFs. It uses **FastAPI** and **pdfplumber** with a pluggable parser architecture to support multiple insurance providers.

### Key Features

✅ **Multi-Insurer Support**: Extensible architecture for multiple insurance providers  
✅ **Auto-Detection**: Automatically identifies the insurance provider  
✅ **RESTful API**: Standard HTTP endpoints for easy integration  
✅ **File Upload**: Accept PDF uploads or server-side file paths  
✅ **Docker Ready**: Containerized for easy deployment  
✅ **Scalable**: Can be deployed on any cloud platform  

---

## Quick Start

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn insurance_parser_api:app --host 0.0.0.0 --port 8000

# Access the API
curl http://localhost:8000/
```

### 2. Docker Deployment

```bash
# Build the image
docker build -t insurance-parser-api .

# Run the container
docker run -d -p 8000:8000 --name insurance-parser insurance-parser-api

# Or use docker-compose
docker-compose up -d
```

### 3. Test the API

```bash
# Health check
curl http://localhost:8000/

# Get supported insurers
curl http://localhost:8000/supported-insurers

# Parse a PDF (upload)
curl -X POST "http://localhost:8000/parse?insurer=auto" \
  -F "file=@/path/to/policy.pdf"

# Parse from server path
curl -X POST "http://localhost:8000/parse-from-path?filepath=/path/to/policy.pdf"
```

---

## API Endpoints

### GET `/`
Health check endpoint

**Response:**
```json
{
  "status": "online",
  "service": "Insurance Policy Parser API",
  "version": "1.0.0"
}
```

### GET `/supported-insurers`
Get list of supported insurance providers

**Response:**
```json
{
  "supported": [
    {
      "id": "discovery",
      "name": "Discovery Insure",
      "status": "fully_supported"
    },
    {
      "id": "santam",
      "name": "Santam",
      "status": "coming_soon"
    }
  ],
  "auto_detect": true
}
```

### POST `/parse`
Parse an uploaded PDF file

**Parameters:**
- `file` (multipart/form-data): PDF file to parse
- `insurer` (query, optional): Insurance provider (`auto`, `discovery`, `santam`, etc.)

**Response:**
```json
{
  "insurer": "Discovery Insure",
  "planNumber": "4000638715",
  "planType": "Classic",
  "currentMonthlyPremium": 4119.89,
  "planholder": {
    "name": "Mr Cedric Percival Keown",
    "email": "cedric.keown@gmail.com"
  },
  "motorVehicles": [...],
  "buildings": [...],
  ...
}
```

### POST `/parse-from-path`
Parse a PDF from a server-side file path

**Parameters:**
- `filepath` (query): Absolute path to PDF file on server
- `insurer` (query, optional): Insurance provider

**Response:** Same as `/parse` endpoint

---

## Architecture

### Parser Strategy Pattern

The service uses a pluggable parser architecture:

```
ParserFactory
    ├── DiscoveryParser (fully implemented)
    ├── SantamParser (stub)
    ├── OldMutualParser (stub)
    └── GenericParser (fallback)
```

### Auto-Detection

When `insurer=auto`, the service:
1. Extracts text from the first few pages
2. Tries each parser's `identify_insurer()` method
3. Uses the first parser that matches
4. Falls back to GenericParser if no match

### Adding New Insurers

To add support for a new insurer:

1. **Create a new parser class:**

```python
class NewInsurerParser(BaseParser):
    def identify_insurer(self) -> str:
        page1 = self.pages_text.get(1, "")
        if "NewInsurer" in page1:
            return "new_insurer"
        return None
    
    def parse(self) -> Dict:
        # Implement parsing logic
        return {
            "insurer": "NewInsurer",
            ...
        }
```

2. **Register in ParserFactory:**

```python
PARSERS = {
    InsurerType.DISCOVERY: DiscoveryParser,
    InsurerType.NEW_INSURER: NewInsurerParser,
    ...
}
```

3. **Add to InsurerType enum:**

```python
class InsurerType(str, Enum):
    DISCOVERY = "discovery"
    NEW_INSURER = "new_insurer"
    ...
```

---

## Deployment Options

### Option 1: Docker on Cloud Platform

**AWS ECS/Fargate:**
```bash
# Build and push to ECR
docker build -t insurance-parser-api .
docker tag insurance-parser-api:latest 123456789.dkr.ecr.region.amazonaws.com/insurance-parser
docker push 123456789.dkr.ecr.region.amazonaws.com/insurance-parser

# Deploy via ECS task definition
```

**Google Cloud Run:**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/insurance-parser-api
gcloud run deploy insurance-parser --image gcr.io/PROJECT_ID/insurance-parser-api --platform managed
```

**Azure Container Apps:**
```bash
az containerapp create \
  --name insurance-parser-api \
  --resource-group myResourceGroup \
  --image insurance-parser-api:latest
```

### Option 2: Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: insurance-parser-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: insurance-parser
  template:
    metadata:
      labels:
        app: insurance-parser
    spec:
      containers:
      - name: api
        image: insurance-parser-api:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: insurance-parser-service
spec:
  selector:
    app: insurance-parser
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Option 3: Serverless (AWS Lambda + API Gateway)

Use **Mangum** adapter for AWS Lambda:

```python
from mangum import Mangum
from insurance_parser_api import app

lambda_handler = Mangum(app)
```

### Option 4: Traditional VPS/VMs

```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with systemd
sudo cp insurance-parser-api.service /etc/systemd/system/
sudo systemctl enable insurance-parser-api
sudo systemctl start insurance-parser-api

# Configure nginx as reverse proxy
sudo cp nginx.conf /etc/nginx/sites-available/insurance-parser
sudo ln -s /etc/nginx/sites-available/insurance-parser /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

---

## Client Integration Examples

### Python

```python
import requests

def parse_policy(pdf_path):
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            'http://localhost:8000/parse',
            files=files,
            params={'insurer': 'auto'}
        )
    return response.json()

result = parse_policy('/path/to/policy.pdf')
print(f"Monthly Premium: R{result['currentMonthlyPremium']}")
```

### JavaScript/TypeScript

```javascript
async function parsePolicyPDF(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('http://localhost:8000/parse?insurer=auto', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}

// Usage in Node.js
const fs = require('fs');
const FormData = require('form-data');
const fetch = require('node-fetch');

const form = new FormData();
form.append('file', fs.createReadStream('/path/to/policy.pdf'));

fetch('http://localhost:8000/parse?insurer=auto', {
    method: 'POST',
    body: form
})
.then(res => res.json())
.then(data => console.log(data));
```

### C# / .NET

```csharp
using System.Net.Http;
using System.Net.Http.Headers;

public async Task<string> ParsePolicyAsync(string filePath)
{
    using var client = new HttpClient();
    using var content = new MultipartFormDataContent();
    
    var fileContent = new ByteArrayContent(File.ReadAllBytes(filePath));
    fileContent.Headers.ContentType = MediaTypeHeaderValue.Parse("application/pdf");
    content.Add(fileContent, "file", Path.GetFileName(filePath));
    
    var response = await client.PostAsync(
        "http://localhost:8000/parse?insurer=auto",
        content
    );
    
    return await response.Content.ReadAsStringAsync();
}
```

### PHP

```php
<?php
$file = '/path/to/policy.pdf';
$cfile = new CURLFile($file, 'application/pdf', basename($file));

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, 'http://localhost:8000/parse?insurer=auto');
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, ['file' => $cfile]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
curl_close($ch);

$data = json_decode($response, true);
echo "Monthly Premium: R" . $data['currentMonthlyPremium'];
?>
```

---

## Performance Considerations

### Optimization Tips

1. **Caching**: Implement Redis caching for frequently accessed PDFs
2. **Async Processing**: Use Celery for background processing of large files
3. **Horizontal Scaling**: Deploy multiple instances behind a load balancer
4. **Database**: Store parsed results in PostgreSQL for quick retrieval
5. **CDN**: Use CDN for static assets and frequently accessed results

### Expected Performance

- **Small PDFs (< 1MB)**: ~1-2 seconds
- **Medium PDFs (1-5MB)**: ~3-5 seconds
- **Large PDFs (5-10MB)**: ~5-10 seconds

### Scaling Recommendations

- **< 100 requests/day**: Single instance sufficient
- **100-1000 requests/day**: 2-3 instances with load balancer
- **1000+ requests/day**: Auto-scaling with 3-10 instances

---

## Security Considerations

### File Upload Security

```python
# Add file size limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Validate file types
ALLOWED_EXTENSIONS = {'.pdf'}

# Scan for malware (optional)
import clamd
cd = clamd.ClamdUnixSocket()
scan_result = cd.scan('/path/to/uploaded/file.pdf')
```

### Authentication

Add API key authentication:

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = "your-secret-api-key"
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/parse")
@limiter.limit("10/minute")
async def parse_policy(...):
    ...
```

---

## Monitoring & Logging

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### Prometheus Metrics

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### Structured Logging

```python
import logging
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
```

---

## Troubleshooting

### Common Issues

**Issue: "ModuleNotFoundError: No module named 'fastapi'"**
```bash
pip install -r requirements.txt
```

**Issue: "Connection refused"**
- Check if server is running: `ps aux | grep uvicorn`
- Check port availability: `netstat -tuln | grep 8000`
- Check firewall rules

**Issue: "PDF parsing errors"**
- Verify PDF is not corrupted: `pdfinfo file.pdf`
- Check PDF version compatibility
- Try with different PDF

**Issue: "Timeout errors"**
- Increase timeout in client
- Check server resources (CPU, memory)
- Consider async processing for large files

---

## Future Enhancements

### Roadmap

- [ ] Support for Santam, Old Mutual, Outsurance
- [ ] Machine Learning for improved extraction accuracy
- [ ] OCR support for scanned documents
- [ ] Batch processing API endpoint
- [ ] WebSocket support for real-time progress
- [ ] Database integration for storing results
- [ ] Admin dashboard for monitoring
- [ ] PDF comparison feature
- [ ] Export to multiple formats (XML, CSV)
- [ ] Multi-language support

---

## Support

For issues or questions:
- Check logs: `tail -f /var/log/insurance-parser/app.log`
- API documentation: `http://localhost:8000/docs`
- OpenAPI spec: `http://localhost:8000/openapi.json`

## License

This project is provided for educational and commercial use.
