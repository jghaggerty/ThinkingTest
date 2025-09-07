# Test Environment Outputs

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.network.vpc_id
}

output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = module.app_lambda.api_gateway_url
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = module.app_lambda.lambda_function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = module.app_lambda.lambda_function_arn
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.network.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = module.network.private_subnet_ids
}

output "environment" {
  description = "Environment name"
  value       = "test"
}
