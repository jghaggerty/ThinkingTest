# App Lambda Module Variables

variable "environment" {
  description = "Environment name (dev, test, stage, prod)"
  type        = string
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
  default     = 30
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 128
}

variable "lambda_environment_variables" {
  description = "Environment variables for Lambda function"
  type        = map(string)
  default     = {}
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for Lambda VPC configuration"
  type        = list(string)
}

variable "lambda_security_group_id" {
  description = "Security group ID for Lambda function"
  type        = string
}

variable "api_stage_name" {
  description = "API Gateway stage name"
  type        = string
  default     = "api"
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
}

variable "dynamodb_table_arn" {
  description = "ARN of DynamoDB table for Lambda permissions"
  type        = string
  default     = null
}

variable "lambda_duration_threshold" {
  description = "Threshold for Lambda duration alarm in milliseconds"
  type        = number
  default     = 5000
}

variable "alarm_actions" {
  description = "List of ARNs for CloudWatch alarm actions"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}
