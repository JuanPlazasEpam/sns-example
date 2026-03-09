variable "aws_region" {
  type        = string
  description = "AWS region to deploy to"
  default     = "us-east-2"
}

variable "project_name" {
  type        = string
  description = "Name prefix for resources"
  default     = "sns-example"
}

