# Variables for app-lambda module

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "thinkingtest"
}

variable "environment" {
  description = "Environment name (dev, test, stage, prod)"
  type        = string
}

variable "lambda_source_path" {
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