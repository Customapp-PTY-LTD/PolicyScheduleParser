#!/bin/bash
# Build and push Docker image to AWS ECR for Lambda deployment
#
# Usage:
#   ./scripts/build-and-push.sh
#
# Prerequisites:
#   - AWS CLI configured with appropriate credentials
#   - Docker installed and running
#
# Environment Variables (set these or they will be prompted):
#   - AWS_ACCOUNT_ID: Your AWS account ID
#   - AWS_REGION: AWS region (default: us-east-1)
#   - ECR_REPO_NAME: ECR repository name (default: insurance-parser)

set -e

# Configuration
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}
AWS_REGION=${AWS_REGION:-us-east-1}
ECR_REPO_NAME=${ECR_REPO_NAME:-insurance-parser}
IMAGE_TAG=${IMAGE_TAG:-latest}

ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
FULL_IMAGE_NAME="${ECR_URI}/${ECR_REPO_NAME}:${IMAGE_TAG}"

echo "=========================================="
echo "Insurance Parser - Lambda Deployment"
echo "=========================================="
echo "AWS Account: ${AWS_ACCOUNT_ID}"
echo "Region: ${AWS_REGION}"
echo "Repository: ${ECR_REPO_NAME}"
echo "Image Tag: ${IMAGE_TAG}"
echo "Full Image: ${FULL_IMAGE_NAME}"
echo "=========================================="

# Check if repository exists, create if not
echo "Checking ECR repository..."
aws ecr describe-repositories --repository-names ${ECR_REPO_NAME} --region ${AWS_REGION} 2>/dev/null || \
    aws ecr create-repository --repository-name ${ECR_REPO_NAME} --region ${AWS_REGION}

# Login to ECR
echo "Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}

# Build the Docker image
echo "Building Docker image..."
docker build -t ${ECR_REPO_NAME}:${IMAGE_TAG} -f Dockerfile .

# Tag the image for ECR
echo "Tagging image for ECR..."
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${FULL_IMAGE_NAME}

# Push to ECR
echo "Pushing image to ECR..."
docker push ${FULL_IMAGE_NAME}

echo "=========================================="
echo "Successfully pushed to ECR!"
echo "Image: ${FULL_IMAGE_NAME}"
echo ""
echo "Next steps:"
echo "1. Create/update Lambda function with this image"
echo "2. Configure API Gateway"
echo "3. Set up Lambda environment variables if needed"
echo "=========================================="

