#!/bin/bash

# AI Bias Psychologist Infrastructure Deployment Script
# This script helps deploy infrastructure to different environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 <environment> <action> [options]"
    echo ""
    echo "Environments:"
    echo "  dev     - Development environment"
    echo "  test    - Test environment"
    echo "  stage   - Staging environment"
    echo "  prod    - Production environment"
    echo ""
    echo "Actions:"
    echo "  init    - Initialize Terraform backend"
    echo "  plan    - Plan infrastructure changes"
    echo "  apply   - Apply infrastructure changes"
    echo "  destroy - Destroy infrastructure (use with caution)"
    echo "  output  - Show Terraform outputs"
    echo ""
    echo "Options:"
    echo "  --auto-approve  - Skip confirmation prompts"
    echo "  --backend-config <file> - Use backend config file"
    echo ""
    echo "Examples:"
    echo "  $0 dev init"
    echo "  $0 dev plan"
    echo "  $0 dev apply --auto-approve"
    echo "  $0 prod plan --backend-config backend.conf"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if terraform is installed
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install Terraform >= 1.0"
        exit 1
    fi
    
    # Check if aws cli is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install AWS CLI"
        exit 1
    fi
    
    # Check if aws credentials are configured
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure'"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to initialize backend
init_backend() {
    local env=$1
    local backend_config=$2
    
    print_status "Initializing Terraform backend for $env environment..."
    
    cd "envs/$env"
    
    if [ -n "$backend_config" ]; then
        terraform init -backend-config="$backend_config"
    else
        print_warning "No backend config provided. You may need to provide backend configuration manually."
        print_warning "Example: terraform init -backend-config='bucket=your-bucket' -backend-config='key=$env/infra.tfstate'"
        terraform init
    fi
    
    cd ../..
    print_success "Backend initialized for $env"
}

# Function to plan infrastructure
plan_infrastructure() {
    local env=$1
    
    print_status "Planning infrastructure for $env environment..."
    
    cd "envs/$env"
    terraform plan -out="$env.tfplan"
    cd ../..
    
    print_success "Plan completed for $env"
}

# Function to apply infrastructure
apply_infrastructure() {
    local env=$1
    local auto_approve=$2
    
    print_status "Applying infrastructure for $env environment..."
    
    cd "envs/$env"
    
    if [ "$auto_approve" = "true" ]; then
        terraform apply -auto-approve "$env.tfplan"
    else
        terraform apply "$env.tfplan"
    fi
    
    cd ../..
    print_success "Infrastructure applied for $env"
}

# Function to destroy infrastructure
destroy_infrastructure() {
    local env=$1
    local auto_approve=$2
    
    print_warning "DESTROYING infrastructure for $env environment!"
    print_warning "This action cannot be undone!"
    
    if [ "$auto_approve" != "true" ]; then
        read -p "Are you sure you want to destroy the $env environment? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            print_status "Destroy cancelled"
            exit 0
        fi
    fi
    
    print_status "Destroying infrastructure for $env environment..."
    
    cd "envs/$env"
    
    if [ "$auto_approve" = "true" ]; then
        terraform destroy -auto-approve
    else
        terraform destroy
    fi
    
    cd ../..
    print_success "Infrastructure destroyed for $env"
}

# Function to show outputs
show_outputs() {
    local env=$1
    
    print_status "Showing outputs for $env environment..."
    
    cd "envs/$env"
    terraform output
    cd ../..
}

# Main script logic
main() {
    # Check if at least 2 arguments are provided
    if [ $# -lt 2 ]; then
        show_usage
        exit 1
    fi
    
    local environment=$1
    local action=$2
    local auto_approve="false"
    local backend_config=""
    
    # Parse additional arguments
    shift 2
    while [[ $# -gt 0 ]]; do
        case $1 in
            --auto-approve)
                auto_approve="true"
                shift
                ;;
            --backend-config)
                backend_config="$2"
                shift 2
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Validate environment
    case $environment in
        dev|test|stage|prod)
            ;;
        *)
            print_error "Invalid environment: $environment"
            show_usage
            exit 1
            ;;
    esac
    
    # Validate action
    case $action in
        init|plan|apply|destroy|output)
            ;;
        *)
            print_error "Invalid action: $action"
            show_usage
            exit 1
            ;;
    esac
    
    # Check if environment directory exists
    if [ ! -d "envs/$environment" ]; then
        print_error "Environment directory 'envs/$environment' does not exist"
        exit 1
    fi
    
    # Check prerequisites
    check_prerequisites
    
    # Execute action
    case $action in
        init)
            init_backend "$environment" "$backend_config"
            ;;
        plan)
            plan_infrastructure "$environment"
            ;;
        apply)
            apply_infrastructure "$environment" "$auto_approve"
            ;;
        destroy)
            destroy_infrastructure "$environment" "$auto_approve"
            ;;
        output)
            show_outputs "$environment"
            ;;
    esac
}

# Run main function with all arguments
main "$@"
