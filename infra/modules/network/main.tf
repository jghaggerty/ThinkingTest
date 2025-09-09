variable "vpc_cidr" {
  description = "CIDR for the VPC (e.g., 10.10.0.0/16)"
  type        = string
}

data "aws_availability_zones" "azs" {
  state = "available"
}

resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "thinkingtest-vpc"
    Environment = var.environment != null ? var.environment : "dev"
  }
}

resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.this.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, 0) # -> /24 if VPC is /16
  availability_zone       = data.aws_availability_zones.azs.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name        = "public-a"
    Environment = var.environment != null ? var.environment : "dev"
    Tier        = "public"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.this.id
  tags = {
    Name = "thinkingtest-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id
  tags = {
    Name = "public-rt"
  }
}

resource "aws_route" "default_inet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "public_a" {
  route_table_id = aws_route_table.public.id
  subnet_id      = aws_subnet.public_a.id
}

# Optional: VPC Flow Logs to CloudWatch (basic observability)
resource "aws_cloudwatch_log_group" "vpc_flow" {
  name              = "/aws/vpc/${aws_vpc.this.id}/flow-logs"
  retention_in_days = 14
}

resource "aws_iam_role" "vpc_flow" {
  name               = "vpc-flow-logs-role"
  assume_role_policy = data.aws_iam_policy_document.vpc_flow_assume.json
}

data "aws_iam_policy_document" "vpc_flow_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals { type = "Service", identifiers = ["vpc-flow-logs.amazonaws.com"] }
  }
}

resource "aws_iam_role_policy" "vpc_flow" {
  role   = aws_iam_role.vpc_flow.id
  policy = data.aws_iam_policy_document.vpc_flow_policy.json
}

data "aws_iam_policy_document" "vpc_flow_policy" {
  statement {
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents", "logs:DescribeLogGroups", "logs:DescribeLogStreams"]
    resources = ["${aws_cloudwatch_log_group.vpc_flow.arn}:*"]
  }
}

resource "aws_flow_log" "vpc" {
  log_destination_type = "cloud-watch-logs"
  log_group_name       = aws_cloudwatch_log_group.vpc_flow.name
  iam_role_arn         = aws_iam_role.vpc_flow.arn
  resource_id          = aws_vpc.this.id
  traffic_type         = "ALL"
}

output "vpc_id" {
  value = aws_vpc.this.id
}
}