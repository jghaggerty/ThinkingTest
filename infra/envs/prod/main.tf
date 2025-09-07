# Production environment configuration for ThinkingTest

terraform {
  required_version = ">= 1.0"
  
  backend "s3" {
    # Backend configuration will be provided via backend config file
    # bucket = "your-terraform-state-bucket"
    # key    = "thinkingtest/prod/terraform.tfstate"
    # region = "us-east-1"
  }
}

# Provider configuration
provider "aws" {
  region = var.aws_region
}

# Local values
locals {
  project_name = "thinkingtest"
  environment  = "prod"
}

# Network module
module "network" {
  source = "../../modules/network"
  
  project_name = local.project_name
  environment  = local.environment
  vpc_cidr     = var.vpc_cidr
  public_subnet_cidr = var.public_subnet_cidr
  availability_zone   = var.availability_zone
}

# App Lambda module
module "app_lambda" {
  source = "../../modules/app-lambda"
  
  project_name = local.project_name
  environment  = local.environment
  lambda_source_path = var.lambda_source_path
  lambda_handler     = var.lambda_handler
  lambda_runtime     = var.lambda_runtime
}