# AWS Lambda Deployment Guide

This guide covers deploying the Insurance Policy Parser API to AWS Lambda.

## Prerequisites

- Docker Desktop installed and running
- AWS CLI configured with appropriate credentials
- AWS account with permissions for Lambda, API Gateway, and ECR

## Quick Start - ZIP Deployment

### 1. Build the Lambda ZIP Package

**PowerShell (Windows):**
```powershell
docker run --rm `
  -v ${PWD}:/var/task `
  -w /var/task `
  --entrypoint /bin/bash `
  public.ecr.aws/lambda/python:3.11 `
  -c "rm -rf build && mkdir build && \
      python -m pip install --upgrade pip && \
      pip install -r requirements.txt -t build && \
      cp insurance_parser_api.py lambda_handler.py document_types.py build/ && \
      cp -r parsers build/parsers && \
      cd build && \
      python -m zipfile -c ../insurance-parser-lambda.zip ."
```

**Bash (Linux/Mac):**
```bash
docker run --rm \
  -v "${PWD}:/var/task" \
  -w /var/task \
  --entrypoint /bin/bash \
  public.ecr.aws/lambda/python:3.11 \
  -c "rm -rf build && mkdir build && \
      python -m pip install --upgrade pip && \
      pip install -r requirements.txt -t build && \
      cp insurance_parser_api.py lambda_handler.py document_types.py build/ && \
      cp -r parsers build/parsers && \
      cd build && \
      python -m zipfile -c ../insurance-parser-lambda.zip ."
```

Or use the provided scripts:
```powershell
.\scripts\build-lambda-zip.ps1
```

### 2. Upload to AWS Lambda

**Option A: Direct Upload (if ZIP < 50MB)**
```bash
aws lambda create-function \
  --function-name insurance-parser \
  --runtime python3.11 \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://insurance-parser-lambda.zip \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
  --timeout 30 \
  --memory-size 512
```

**Option B: Upload via S3 (if ZIP > 50MB)**
```bash
# Upload to S3
aws s3 cp insurance-parser-lambda.zip s3://your-bucket/lambda/insurance-parser-lambda.zip

# Create Lambda function from S3
aws lambda create-function \
  --function-name insurance-parser \
  --runtime python3.11 \
  --handler lambda_handler.lambda_handler \
  --code S3Bucket=your-bucket,S3Key=lambda/insurance-parser-lambda.zip \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
  --timeout 30 \
  --memory-size 512
```

### 3. Update Existing Lambda
```bash
aws lambda update-function-code \
  --function-name insurance-parser \
  --zip-file fileb://insurance-parser-lambda.zip
```

## Lambda Configuration

### Recommended Settings

| Setting | Value | Notes |
|---------|-------|-------|
| Runtime | Python 3.11 | Required |
| Handler | `lambda_handler.lambda_handler` | Required |
| Timeout | 30 seconds | PDF processing can take time |
| Memory | 512 MB | Increase if processing large PDFs |
| Ephemeral Storage | 512 MB | Default, increase if needed |

### Environment Variables (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |

### IAM Role Permissions

The Lambda execution role needs:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

## API Gateway Setup

### Create REST API

1. Go to API Gateway console
2. Create REST API
3. Create resources and methods:

```
/                           GET     → Lambda (health check)
/document-types             GET     → Lambda
/document-type/{guid}       GET     → Lambda
/parse                      POST    → Lambda
/parse-json                 POST    → Lambda
/parse-from-url             POST    → Lambda
/supported-insurers         GET     → Lambda
```

### Configure Lambda Proxy Integration

For each method:
1. Integration type: Lambda Function
2. Use Lambda Proxy integration: ✓ (checked)
3. Lambda Function: insurance-parser

### Deploy API

1. Actions → Deploy API
2. Create new stage (e.g., "prod")
3. Note the Invoke URL

## Testing

### Test Lambda Directly
```bash
aws lambda invoke \
  --function-name insurance-parser \
  --payload '{"httpMethod":"GET","path":"/"}' \
  response.json

cat response.json
```

### Test via API Gateway
```bash
# Health check
curl https://YOUR_API_ID.execute-api.REGION.amazonaws.com/prod/

# Get document types
curl https://YOUR_API_ID.execute-api.REGION.amazonaws.com/prod/document-types

# Parse PDF from URL
curl -X POST https://YOUR_API_ID.execute-api.REGION.amazonaws.com/prod/parse-from-url \
  -H "Content-Type: application/json" \
  -d '{"pdf_url": "https://example.com/policy.pdf", "document_guid": "auto-d3t3-ct00-0000"}'
```

## Troubleshooting

### Common Issues

**1. Timeout errors**
- Increase Lambda timeout (up to 15 minutes max)
- Increase memory allocation

**2. Import errors**
- Ensure all files are in the ZIP root
- Check that parsers/ directory is included

**3. "Task timed out" for large PDFs**
- Increase memory to 1024 MB or more
- Consider using async processing with S3

### View Logs
```bash
aws logs tail /aws/lambda/insurance-parser --follow
```

## Files Included in ZIP

```
insurance-parser-lambda.zip
├── insurance_parser_api.py    # FastAPI application
├── lambda_handler.py          # Lambda entry point
├── document_types.py          # Document GUID registry
├── parsers/                   # Parser package
│   ├── __init__.py
│   ├── base_parser.py
│   ├── discovery_parser.py
│   ├── santam_parser.py
│   └── generic_parser.py
└── [dependencies]             # All pip packages
```

## Alternative: Container Image Deployment

If the ZIP file is too large or you prefer containers:

```bash
# Build image
docker build -t insurance-parser .

# Tag for ECR
docker tag insurance-parser:latest YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/insurance-parser:latest

# Login and push
aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com
docker push YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/insurance-parser:latest

# Create Lambda from image
aws lambda create-function \
  --function-name insurance-parser \
  --package-type Image \
  --code ImageUri=YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/insurance-parser:latest \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role
```
