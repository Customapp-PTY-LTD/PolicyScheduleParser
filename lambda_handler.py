"""
AWS Lambda Handler for Insurance Policy Parser API

This module wraps the FastAPI application with Mangum to make it
compatible with AWS Lambda and API Gateway.

Deployment:
    - Build Docker image: docker build -t insurance-parser .
    - Push to ECR and deploy to Lambda
    - Configure API Gateway to route to Lambda

Environment Variables (optional):
    - LOG_LEVEL: Logging level (default: INFO)
"""

import logging
import os

# Configure logging for Lambda
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the FastAPI app
from insurance_parser_api import app

# Import Mangum for Lambda/API Gateway compatibility
from mangum import Mangum

# Create the Lambda handler
# Mangum handles the translation between API Gateway events and ASGI
lambda_handler = Mangum(
    app,
    lifespan="off",  # Disable lifespan events for Lambda
    api_gateway_base_path=None  # Set if using custom domain with base path
)


def handler(event, context):
    """
    Alternative handler function name for Lambda.
    
    Use this if you configure Lambda with handler: lambda_handler.handler
    instead of lambda_handler.lambda_handler
    """
    logger.info(f"Received event: {event.get('httpMethod', 'Unknown')} {event.get('path', '/')}")
    return lambda_handler(event, context)
