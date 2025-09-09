# Variables for development environment

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"
}

variable "vpc_cidr" {
  description = "CIDR for the VPC (e.g., 10.10.0.0/16)"
  type        = string
  default     = "10.10.0.0/16"
}