# Outputs for staging environment

output "api_url" {
  description = "URL of the API Gateway"
  value       = module.app_lambda.api_url
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.network.vpc_id
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = module.app_lambda.lambda_function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = module.app_lambda.lambda_function_arn
}