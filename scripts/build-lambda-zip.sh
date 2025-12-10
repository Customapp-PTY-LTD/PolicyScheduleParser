#!/bin/bash
# Build Lambda ZIP package using Docker
#
# Usage:
#   ./scripts/build-lambda-zip.sh
#
# This creates insurance-parser-lambda.zip ready for Lambda deployment

set -e

echo "=========================================="
echo "Building Lambda ZIP Package"
echo "=========================================="

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

ZIP_SIZE=$(du -h insurance-parser-lambda.zip | cut -f1)

echo "=========================================="
echo "SUCCESS: Created insurance-parser-lambda.zip"
echo "Size: ${ZIP_SIZE}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Upload to S3 or directly to Lambda"
echo "2. Set handler to: lambda_handler.lambda_handler"
echo "3. Configure API Gateway"

