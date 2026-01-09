variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}

variable "connect_instance_alias" {
  description = "Amazon Connect Instance Alias (must be unique)"
  type        = string
  default     = "counter-demo"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}
