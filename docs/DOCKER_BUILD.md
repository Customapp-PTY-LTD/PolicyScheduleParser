# Building for AWS Lambda with Docker

This guide explains how to build the Insurance Parser API as a deployment package for AWS Lambda using Docker.

## Prerequisites

- **Docker Desktop** installed and running
- AWS CLI configured (for deployment)
- PowerShell (Windows) or Bash (Linux/Mac)

## Why Use Docker?

AWS Lambda runs on Amazon Linux. Building the deployment package inside a Docker container that matches the Lambda runtime ensures:

- Native dependencies (like `pdfplumber`, `cryptography`) are compiled for the correct architecture
- All dependencies are compatible with the Lambda execution environment
- Consistent builds across different development machines

## Quick Build Command

### Windows (PowerShell)

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

### Linux/Mac (Bash)

```bash
docker run --rm \
  -v $(pwd):/var/task \
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

## Command Breakdown

| Part | Description |
|------|-------------|
| `docker run --rm` | Run container and remove it after completion |
| `-v ${PWD}:/var/task` | Mount current directory to `/var/task` in container |
| `-w /var/task` | Set working directory inside container |
| `--entrypoint /bin/bash` | Override default entrypoint to use bash |
| `public.ecr.aws/lambda/python:3.11` | Official AWS Lambda Python 3.11 image |
| `-c "..."` | Execute the build commands |

## Build Steps Explained

1. **Clean previous build**
   ```bash
   rm -rf build && mkdir build
   ```

2. **Upgrade pip**
   ```bash
   python -m pip install --upgrade pip
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt -t build
   ```
   The `-t build` flag installs packages directly into the `build/` directory.

4. **Copy application files**
   ```bash
   cp insurance_parser_api.py lambda_handler.py document_types.py build/
   cp -r parsers build/parsers
   ```

5. **Create ZIP archive**
   ```bash
   cd build && python -m zipfile -c ../insurance-parser-lambda.zip .
   ```

## Output

After successful execution:

```
insurance-parser-lambda.zip  (~39 MB)
```

### Package Contents

```
insurance-parser-lambda.zip
├── insurance_parser_api.py    # FastAPI application
├── lambda_handler.py          # Lambda entry point (Mangum adapter)
├── document_types.py          # Document GUIDs and parser registry
├── parsers/                   # Parser modules
│   ├── __init__.py
│   ├── base_parser.py
│   ├── discovery_parser.py
│   ├── hollard_parser.py
│   ├── santam_parser.py
│   └── generic_parser.py
└── [dependencies]/            # All pip packages
    ├── fastapi/
    ├── pdfplumber/
    ├── mangum/
    └── ...
```

## Deploying to AWS Lambda

### Create New Function

```bash
aws lambda create-function \
  --function-name insurance-parser \
  --runtime python3.11 \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://insurance-parser-lambda.zip \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_LAMBDA_ROLE \
  --timeout 30 \
  --memory-size 512
```

### Update Existing Function

```bash
aws lambda update-function-code \
  --function-name insurance-parser \
  --zip-file fileb://insurance-parser-lambda.zip
```

### Lambda Configuration

| Setting | Recommended Value |
|---------|-------------------|
| Runtime | Python 3.11 |
| Handler | `lambda_handler.lambda_handler` |
| Timeout | 30 seconds |
| Memory | 512 MB |
| Architecture | x86_64 |

## Testing the Deployment

### Invoke via AWS CLI

```bash
# Health check
aws lambda invoke \
  --function-name insurance-parser \
  --payload '{"httpMethod":"GET","path":"/"}' \
  response.json && cat response.json

# Parse a document
aws lambda invoke \
  --function-name insurance-parser \
  --payload '{
    "httpMethod": "POST",
    "path": "/parse-from-url",
    "headers": {"Content-Type": "application/json"},
    "body": "{\"pdf_url\": \"https://example.com/policy.pdf\", \"document_guid\": \"auto-d3t3-ct00-0000\"}"
  }' \
  response.json && cat response.json
```

## Troubleshooting

### Docker not running

```
error during connect: ... open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

**Solution:** Start Docker Desktop and wait for it to initialize.

### Permission denied on Linux/Mac

```bash
# Add your user to the docker group
sudo usermod -aG docker $USER
# Log out and back in, or run:
newgrp docker
```

### Package too large (>50MB)

If dependencies push the ZIP over 50MB, you have two options:

1. **Use Lambda Layers** - Split dependencies into a layer
2. **Use Container Image** - Build a Docker image and deploy to Lambda

### Import errors in Lambda

Ensure all files are copied correctly:

```bash
# Verify ZIP contents
python -m zipfile -l insurance-parser-lambda.zip | head -50
```

## Alternative: Using the Build Script

For convenience, use the provided PowerShell script:

```powershell
.\scripts\build-lambda-zip.ps1
```

Or Bash script:

```bash
./scripts/build-lambda-zip.sh
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Lambda Package

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Lambda ZIP
        run: |
          docker run --rm \
            -v ${{ github.workspace }}:/var/task \
            -w /var/task \
            --entrypoint /bin/bash \
            public.ecr.aws/lambda/python:3.11 \
            -c "rm -rf build && mkdir build && \
                pip install -r requirements.txt -t build && \
                cp insurance_parser_api.py lambda_handler.py document_types.py build/ && \
                cp -r parsers build/parsers && \
                cd build && \
                python -m zipfile -c ../insurance-parser-lambda.zip ."
      
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: lambda-package
          path: insurance-parser-lambda.zip
```

## References

- [AWS Lambda Python Runtime](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [AWS Lambda Container Images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [Mangum - ASGI Adapter for Lambda](https://mangum.io/)

