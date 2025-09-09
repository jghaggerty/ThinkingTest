# Development environment configuration for ThinkingTest

terraform {
  required_version = ">= 1.0"
  
  backend "s3" {
    bucket         = "thinkingtest-tfstate"  # or your unique bucket
    key            = "dev/infra.tfstate"
    region         = "us-east-2"
    encrypt        = true
  }
}

# Provider configuration
provider "aws" {
  region = var.aws_region
}

# Local values
locals {
  project_name = "thinkingtest"
  environment  = "dev"
}

# Network module
module "network" {
  source = "../../modules/network"
  
  environment = local.environment
  vpc_cidr    = var.vpc_cidr
}

