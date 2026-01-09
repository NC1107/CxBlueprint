terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

# Amazon Connect Instance

resource "aws_connect_instance" "counter_demo" {
  identity_management_type = "CONNECT_MANAGED"
  inbound_calls_enabled    = true
  outbound_calls_enabled   = false
  instance_alias           = var.connect_instance_alias
  
  tags = {
    Name        = "Counter Demo"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Lambda Function

data "archive_file" "counter_lambda" {
  type        = "zip"
  source_file = "${path.module}/../lambda/counter.py"
  output_path = "${path.module}/counter_lambda.zip"
}

resource "aws_iam_role" "counter_lambda_role" {
  name = "${var.connect_instance_alias}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.counter_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "counter" {
  filename         = data.archive_file.counter_lambda.output_path
  function_name    = "${var.connect_instance_alias}-counter"
  role            = aws_iam_role.counter_lambda_role.arn
  handler         = "counter.lambda_handler"
  source_code_hash = data.archive_file.counter_lambda.output_base64sha256
  runtime         = "python3.11"
  timeout         = 10

  tags = {
    Name        = "Counter Lambda"
    Environment = var.environment
  }
}

resource "aws_lambda_permission" "allow_connect" {
  statement_id  = "AllowExecutionFromConnect"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.counter.function_name
  principal     = "connect.amazonaws.com"
  source_arn    = aws_connect_instance.counter_demo.arn
}

resource "aws_connect_lambda_function_association" "counter" {
  instance_id  = aws_connect_instance.counter_demo.id
  function_arn = aws_lambda_function.counter.arn
}

# Contact Flow

locals {
  flow_json = templatefile("${path.module}/../counter_flow.json", {
    COUNTER_LAMBDA_ARN = aws_lambda_function.counter.arn
  })
}

resource "aws_connect_contact_flow" "counter_flow" {
  instance_id = aws_connect_instance.counter_demo.id
  name        = "Counter Flow"
  description = "Increments counter and speaks the value"
  type        = "CONTACT_FLOW"
  content     = local.flow_json

  tags = {
    Name        = "Counter Flow"
    Environment = var.environment
  }
  
  depends_on = [
    aws_connect_lambda_function_association.counter
  ]
}
