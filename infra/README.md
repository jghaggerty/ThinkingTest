# AI Bias Psychologist Infrastructure

This directory contains the Terraform infrastructure code for the AI Bias Psychologist application, organized in a multi-environment setup.

## Directory Structure

```
infra/
├── envs/                    # Environment-specific configurations
│   ├── dev/                # Development environment
│   ├── test/               # Test environment
│   ├── stage/              # Staging environment
│   └── prod/               # Production environment
└── modules/                # Reusable Terraform modules
    ├── network/            # VPC, subnets, gateways
    └── app-lambda/         # Lambda functions and API Gateway
```

## Architecture

Each environment is completely isolated and includes:

- **VPC** with public and private subnets across multiple AZs
- **Internet Gateway** and **NAT Gateways** for internet access
- **Lambda function** in private subnets with VPC access
- **API Gateway** for HTTP API endpoints
- **CloudWatch** logging and monitoring
- **Security Groups** for network access control

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** >= 1.0 installed
3. **S3 bucket** for Terraform state storage
4. **DynamoDB table** for state locking (optional but recommended)

## Deployment

### 1. Initialize Backend

For each environment, initialize the Terraform backend:

```bash
# Development
cd infra/envs/dev
terraform init -backend-config="bucket=your-terraform-state-bucket" \
               -backend-config="key=dev/infra.tfstate" \
               -backend-config="region=us-east-1"

# Test
cd infra/envs/test
terraform init -backend-config="bucket=your-terraform-state-bucket" \
               -backend-config="key=test/infra.tfstate" \
               -backend-config="region=us-east-1"

# Staging
cd infra/envs/stage
terraform init -backend-config="bucket=your-terraform-state-bucket" \
               -backend-config="key=stage/infra.tfstate" \
               -backend-config="region=us-east-1"

# Production
cd infra/envs/prod
terraform init -backend-config="bucket=your-terraform-state-bucket" \
               -backend-config="key=prod/infra.tfstate" \
               -backend-config="region=us-east-1"
```

### 2. Plan and Apply

```bash
# Development
cd infra/envs/dev
terraform plan
terraform apply

# Test
cd infra/envs/test
terraform plan
terraform apply

# Staging
cd infra/envs/stage
terraform plan
terraform apply

# Production
cd infra/envs/prod
terraform plan
terraform apply
```

## Environment Differences

| Environment | VPC CIDR | Lambda Memory | Timeout | Log Retention |
|-------------|----------|---------------|---------|---------------|
| dev         | 10.0.0.0/16 | 128 MB | 30s | 7 days |
| test        | 10.1.0.0/16 | 256 MB | 30s | 14 days |
| stage       | 10.2.0.0/16 | 512 MB | 60s | 30 days |
| prod        | 10.3.0.0/16 | 1024 MB | 300s | 90 days |

## API Endpoints

After deployment, each environment will have the following API endpoints:

- `GET /` - Health check
- `GET /api/health` - API health check
- `GET /api/probes` - List all probes
- `POST /api/probes` - Create a new probe
- `GET /api/probes/{id}` - Get specific probe
- `PUT /api/probes/{id}` - Update probe
- `DELETE /api/probes/{id}` - Delete probe
- `GET /api/responses` - List responses
- `POST /api/responses` - Create response
- `GET /api/analytics` - Get analytics data

## Monitoring

Each environment includes:

- **CloudWatch Logs** for Lambda function logs
- **CloudWatch Alarms** for Lambda errors and duration
- **API Gateway** access logs (can be enabled)

## Security

- Lambda functions run in private subnets
- Security groups restrict network access
- IAM roles follow least privilege principle
- All resources are tagged for cost tracking and management

## Cost Optimization

- Different instance sizes per environment
- Shorter log retention in non-production
- NAT Gateways only in environments that need them
- Appropriate Lambda memory allocation per environment

## Troubleshooting

### Common Issues

1. **Backend initialization fails**: Ensure S3 bucket exists and you have proper permissions
2. **Lambda deployment fails**: Check that the `app/lambda` directory exists and contains valid Python code
3. **VPC limits**: Ensure you haven't exceeded VPC limits in your AWS account
4. **Subnet CIDR conflicts**: Each environment uses different CIDR blocks to avoid conflicts

### Useful Commands

```bash
# Check Terraform state
terraform state list

# Import existing resources
terraform import aws_vpc.main vpc-xxxxxxxxx

# Destroy environment (use with caution)
terraform destroy

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive
```

## Contributing

When making changes to the infrastructure:

1. Test changes in the `dev` environment first
2. Use `terraform plan` to review changes before applying
3. Update this README if you add new resources or change the architecture
4. Ensure all environments are consistent in structure
