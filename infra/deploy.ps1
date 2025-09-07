# AI Bias Psychologist Infrastructure Deployment Script
# This PowerShell script helps deploy infrastructure to different environments

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "test", "stage", "prod")]
    [string]$Environment,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet("init", "plan", "apply", "destroy", "output")]
    [string]$Action,
    
    [switch]$AutoApprove,
    [string]$BackendConfig
)

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to show usage
function Show-Usage {
    Write-Host "Usage: .\deploy.ps1 -Environment <env> -Action <action> [options]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Environments:" -ForegroundColor Cyan
    Write-Host "  dev     - Development environment"
    Write-Host "  test    - Test environment"
    Write-Host "  stage   - Staging environment"
    Write-Host "  prod    - Production environment"
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Cyan
    Write-Host "  init    - Initialize Terraform backend"
    Write-Host "  plan    - Plan infrastructure changes"
    Write-Host "  apply   - Apply infrastructure changes"
    Write-Host "  destroy - Destroy infrastructure (use with caution)"
    Write-Host "  output  - Show Terraform outputs"
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  -AutoApprove     - Skip confirmation prompts"
    Write-Host "  -BackendConfig   - Use backend config file"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\deploy.ps1 -Environment dev -Action init"
    Write-Host "  .\deploy.ps1 -Environment dev -Action plan"
    Write-Host "  .\deploy.ps1 -Environment dev -Action apply -AutoApprove"
    Write-Host "  .\deploy.ps1 -Environment prod -Action plan -BackendConfig backend.conf"
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    # Check if terraform is installed
    try {
        $null = Get-Command terraform -ErrorAction Stop
    }
    catch {
        Write-Error "Terraform is not installed. Please install Terraform >= 1.0"
        exit 1
    }
    
    # Check if aws cli is installed
    try {
        $null = Get-Command aws -ErrorAction Stop
    }
    catch {
        Write-Error "AWS CLI is not installed. Please install AWS CLI"
        exit 1
    }
    
    # Check if aws credentials are configured
    try {
        $null = aws sts get-caller-identity 2>$null
    }
    catch {
        Write-Error "AWS credentials not configured. Please run 'aws configure'"
        exit 1
    }
    
    Write-Success "Prerequisites check passed"
}

# Function to initialize backend
function Initialize-Backend {
    param([string]$Env, [string]$Config)
    
    Write-Status "Initializing Terraform backend for $Env environment..."
    
    Push-Location "envs\$Env"
    
    try {
        if ($Config) {
            terraform init -backend-config="$Config"
        }
        else {
            Write-Warning "No backend config provided. You may need to provide backend configuration manually."
            Write-Warning "Example: terraform init -backend-config='bucket=your-bucket' -backend-config='key=$Env/infra.tfstate'"
            terraform init
        }
        Write-Success "Backend initialized for $Env"
    }
    finally {
        Pop-Location
    }
}

# Function to plan infrastructure
function Invoke-InfrastructurePlan {
    param([string]$Env)
    
    Write-Status "Planning infrastructure for $Env environment..."
    
    Push-Location "envs\$Env"
    
    try {
        terraform plan -out="$Env.tfplan"
        Write-Success "Plan completed for $Env"
    }
    finally {
        Pop-Location
    }
}

# Function to apply infrastructure
function Invoke-InfrastructureApply {
    param([string]$Env, [bool]$AutoApprove)
    
    Write-Status "Applying infrastructure for $Env environment..."
    
    Push-Location "envs\$Env"
    
    try {
        if ($AutoApprove) {
            terraform apply -auto-approve "$Env.tfplan"
        }
        else {
            terraform apply "$Env.tfplan"
        }
        Write-Success "Infrastructure applied for $Env"
    }
    finally {
        Pop-Location
    }
}

# Function to remove infrastructure
function Remove-Infrastructure {
    param([string]$Env, [bool]$AutoApprove)
    
    Write-Warning "REMOVING infrastructure for $Env environment!"
    Write-Warning "This action cannot be undone!"
    
    if (-not $AutoApprove) {
        $confirm = Read-Host "Are you sure you want to remove the $Env environment? (yes/no)"
        if ($confirm -ne "yes") {
            Write-Status "Remove cancelled"
            return
        }
    }
    
    Write-Status "Removing infrastructure for $Env environment..."
    
    Push-Location "envs\$Env"
    
    try {
        if ($AutoApprove) {
            terraform destroy -auto-approve
        }
        else {
            terraform destroy
        }
        Write-Success "Infrastructure removed for $Env"
    }
    finally {
        Pop-Location
    }
}

# Function to show outputs
function Show-Outputs {
    param([string]$Env)
    
    Write-Status "Showing outputs for $Env environment..."
    
    Push-Location "envs\$Env"
    
    try {
        terraform output
    }
    finally {
        Pop-Location
    }
}

# Main script logic
function Main {
    # Check if environment directory exists
    if (-not (Test-Path "envs\$Environment")) {
        Write-Error "Environment directory 'envs\$Environment' does not exist"
        exit 1
    }
    
    # Check prerequisites
    Test-Prerequisites
    
    # Execute action
    switch ($Action) {
        "init" {
            Initialize-Backend -Env $Environment -Config $BackendConfig
        }
        "plan" {
            Invoke-InfrastructurePlan -Env $Environment
        }
        "apply" {
            Invoke-InfrastructureApply -Env $Environment -AutoApprove $AutoApprove
        }
        "destroy" {
            Remove-Infrastructure -Env $Environment -AutoApprove $AutoApprove
        }
        "output" {
            Show-Outputs -Env $Environment
        }
    }
}

# Run main function
Main
