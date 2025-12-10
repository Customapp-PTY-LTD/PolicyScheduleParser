# Build Lambda ZIP package using Docker
#
# Usage:
#   .\scripts\build-lambda-zip.ps1
#
# This creates insurance-parser-lambda.zip ready for Lambda deployment

Write-Host "=========================================="
Write-Host "Building Lambda ZIP Package"
Write-Host "=========================================="

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

if ($LASTEXITCODE -eq 0) {
    $zipSize = (Get-Item insurance-parser-lambda.zip).Length / 1MB
    Write-Host "=========================================="
    Write-Host "SUCCESS: Created insurance-parser-lambda.zip"
    Write-Host "Size: $([math]::Round($zipSize, 2)) MB"
    Write-Host "=========================================="
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Upload to S3 or directly to Lambda"
    Write-Host "2. Set handler to: lambda_handler.lambda_handler"
    Write-Host "3. Configure API Gateway"
} else {
    Write-Host "ERROR: Build failed"
    exit 1
}

