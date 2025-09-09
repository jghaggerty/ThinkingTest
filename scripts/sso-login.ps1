# AWS SSO Login Helper Script
# Usage: .\scripts\sso-login.ps1 -Profile "dev-sso" -Region "us-east-2"

param(
    [string]$Profile = "dev-sso",
    [string]$Region = "us-east-2"
)

Write-Host "🔐 AWS SSO Login Helper" -ForegroundColor Cyan
Write-Host "Profile: $Profile" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow
Write-Host ""

# Check if AWS CLI is available
try {
    $awsVersion = aws --version 2>$null
    Write-Host "✅ AWS CLI found: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install AWS CLI v2 first." -ForegroundColor Red
    Write-Host "   Download from: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    exit 1
}

# Perform SSO login
Write-Host "🔑 Logging into AWS SSO..." -ForegroundColor Cyan
try {
    aws sso login --profile $Profile
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SSO login successful!" -ForegroundColor Green
    } else {
        Write-Host "❌ SSO login failed. Please check your credentials and try again." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error during SSO login: $_" -ForegroundColor Red
    exit 1
}

# Set environment variables
Write-Host "🌍 Setting environment variables..." -ForegroundColor Cyan
$env:AWS_PROFILE = $Profile
$env:AWS_DEFAULT_REGION = $Region

Write-Host ""
Write-Host "✅ Authentication complete!" -ForegroundColor Green
Write-Host "   AWS_PROFILE = $($env:AWS_PROFILE)" -ForegroundColor Yellow
Write-Host "   AWS_DEFAULT_REGION = $($env:AWS_DEFAULT_REGION)" -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 You can now run Terraform commands:" -ForegroundColor Cyan
Write-Host "   cd infra/envs/dev" -ForegroundColor White
Write-Host "   terraform init" -ForegroundColor White
Write-Host "   terraform plan" -ForegroundColor White
Write-Host "   terraform apply" -ForegroundColor White
