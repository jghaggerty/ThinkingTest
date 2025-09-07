# Staging Environment Variables

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.2.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.2.1.0/24", "10.2.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.2.10.0/24", "10.2.20.0/24"]
}

variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "api-handler"
}

variable "lambda_source_dir" {
  description = "Path to the Lambda function source code"
  type        = string
  default     = "../../../app/lambda"
}

variable "lambda_handler" {
  description = "Lambda function handler"
  type        = string
  default     = "handler.lambda_handler"
}

variable "lambda_runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.11"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 60
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 512
}

variable "api_stage_name" {
  description = "API Gateway stage name"
  type        = string
  default     = "stage"
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

variable "app_version" {
  description = "Application version"
  type        = string
  default     = "1.0.0"
}
