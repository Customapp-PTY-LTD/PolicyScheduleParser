# Build and push Docker image to AWS ECR for Lambda deployment (PowerShell)
#
# Usage:
#   .\scripts\build-and-push.ps1
#
# Prerequisites:
#   - AWS CLI configured with appropriate credentials
#   - Docker installed and running
#
# Parameters (optional):
#   -AwsRegion: AWS region (default: us-east-1)
#   -EcrRepoName: ECR repository name (default: insurance-parser)
#   -ImageTag: Image tag (default: latest)

param(
    [string]$AwsRegion = "us-east-1",
    [string]$EcrRepoName = "insurance-parser",
    [string]$ImageTag = "latest"
)

$ErrorActionPreference = "Stop"

# Get AWS Account ID
Write-Host "Getting AWS Account ID..."
$AwsAccountId = aws sts get-caller-identity --query Account --output text
if (-not $AwsAccountId) {
    Write-Error "Failed to get AWS Account ID. Make sure AWS CLI is configured."
    exit 1
}

$EcrUri = "$AwsAccountId.dkr.ecr.$AwsRegion.amazonaws.com"
$FullImageName = "$EcrUri/${EcrRepoName}:$ImageTag"

Write-Host "=========================================="
Write-Host "Insurance Parser - Lambda Deployment"
Write-Host "=========================================="
Write-Host "AWS Account: $AwsAccountId"
Write-Host "Region: $AwsRegion"
Write-Host "Repository: $EcrRepoName"
Write-Host "Image Tag: $ImageTag"
Write-Host "Full Image: $FullImageName"
Write-Host "=========================================="

# Check if repository exists, create if not
Write-Host "Checking ECR repository..."
try {
    aws ecr describe-repositories --repository-names $EcrRepoName --region $AwsRegion 2>$null
} catch {
    Write-Host "Creating ECR repository..."
    aws ecr create-repository --repository-name $EcrRepoName --region $AwsRegion
}

# Login to ECR
Write-Host "Logging into ECR..."
$loginPassword = aws ecr get-login-password --region $AwsRegion
$loginPassword | docker login --username AWS --password-stdin $EcrUri

# Build the Docker image
Write-Host "Building Docker image..."
docker build -t "${EcrRepoName}:$ImageTag" -f Dockerfile .

if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker build failed"
    exit 1
}

# Tag the image for ECR
Write-Host "Tagging image for ECR..."
docker tag "${EcrRepoName}:$ImageTag" $FullImageName

# Push to ECR
Write-Host "Pushing image to ECR..."
docker push $FullImageName

if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker push failed"
    exit 1
}

Write-Host "=========================================="
Write-Host "Successfully pushed to ECR!"
Write-Host "Image: $FullImageName"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Create/update Lambda function with this image"
Write-Host "2. Configure API Gateway"
Write-Host "3. Set up Lambda environment variables if needed"
Write-Host "=========================================="

