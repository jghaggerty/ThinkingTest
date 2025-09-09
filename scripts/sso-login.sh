#!/bin/bash
# AWS SSO Login Helper Script
# Usage: ./scripts/sso-login.sh [profile] [region]

set -e

# Default values
PROFILE=${1:-"dev-sso"}
REGION=${2:-"us-east-2"}

echo "🔐 AWS SSO Login Helper"
echo "Profile: $PROFILE"
echo "Region: $REGION"
echo ""

# Check if AWS CLI is available
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI v2 first."
    echo "   Download from: https://aws.amazon.com/cli/"
    exit 1
fi

AWS_VERSION=$(aws --version 2>&1)
echo "✅ AWS CLI found: $AWS_VERSION"

# Perform SSO login
echo "🔑 Logging into AWS SSO..."
if aws sso login --profile "$PROFILE"; then
    echo "✅ SSO login successful!"
else
    echo "❌ SSO login failed. Please check your credentials and try again."
    exit 1
fi

# Set environment variables
echo "🌍 Setting environment variables..."
export AWS_PROFILE="$PROFILE"
export AWS_DEFAULT_REGION="$REGION"

echo ""
echo "✅ Authentication complete!"
echo "   AWS_PROFILE = $AWS_PROFILE"
echo "   AWS_DEFAULT_REGION = $AWS_DEFAULT_REGION"
echo ""
echo "🚀 You can now run Terraform commands:"
echo "   cd infra/envs/dev"
echo "   terraform init"
echo "   terraform plan"
echo "   terraform apply"
