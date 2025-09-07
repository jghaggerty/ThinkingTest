# Production Environment Configuration
# This file configures the production environment infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    # Backend configuration will be provided via terraform init -backend-config
    # Example: terraform init -backend-config="bucket=your-terraform-state-bucket" -backend-config="key=prod/infra.tfstate" -backend-config="region=us-east-1"
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = "prod"
      Project     = "ai-bias-psychologist"
      ManagedBy   = "terraform"
    }
  }
}

# Local values
locals {
  environment = "prod"
  common_tags = {
    Environment = local.environment
    Project     = "ai-bias-psychologist"
    ManagedBy   = "terraform"
  }
}

# Network Module
module "network" {
  source = "../../modules/network"
  
  environment = local.environment
  vpc_cidr    = var.vpc_cidr
  
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  
  tags = local.common_tags
}

# App Lambda Module
module "app_lambda" {
  source = "../../modules/app-lambda"
  
  environment = local.environment
  function_name = var.function_name
  
  lambda_source_dir = var.lambda_source_dir
  lambda_handler    = var.lambda_handler
  lambda_runtime    = var.lambda_runtime
  lambda_timeout    = var.lambda_timeout
  lambda_memory_size = var.lambda_memory_size
  
  lambda_environment_variables = {
    ENVIRONMENT = local.environment
    APP_VERSION = var.app_version
    LOG_LEVEL   = "WARNING"
  }
  
  private_subnet_ids        = module.network.private_subnet_ids
  lambda_security_group_id  = module.network.lambda_security_group_id
  
  api_stage_name = var.api_stage_name
  log_retention_days = var.log_retention_days
  
  tags = local.common_tags
}
