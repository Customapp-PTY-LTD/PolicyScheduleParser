# Dockerfile for Insurance Policy Parser API - AWS Lambda Deployment
# Uses AWS Lambda Python base image for compatibility

FROM public.ecr.aws/lambda/python:3.11

# Set working directory to Lambda task root
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY insurance_parser_api.py .
COPY lambda_handler.py .
COPY document_types.py .

# Copy parsers package
COPY parsers/ ./parsers/

# Set the Lambda handler
CMD ["lambda_handler.lambda_handler"]
