# Variables for network module

variable "environment" {
  description = "Environment name (dev, test, stage, prod)"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR for the VPC (e.g., 10.10.0.0/16)"
  type        = string
}