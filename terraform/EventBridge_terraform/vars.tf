variable "IAM_ROLE_NAME" {
  description = "The name of the IAM role"
  type        = string
}

variable "IAM_POLICY" {
  description = "The name of the IAM policy"
  type        = string
}

variable "EVENT_RULE" {
  description = "The name of the CloudWatch Event Rule"
  type        = string
}

variable "BUCKET_NAME" {
  description = "The name of the S3 bucket"
  type        = string
}

variable "FILE_NAME" {
  description = "The name of the file in the S3 bucket"
  type        = string
}

variable "ECS_TASK" {
  description = "The ECS task definition"
  type        = string
}

variable "CLUSTER_ARN" {
  description = "The ARN of the ECS cluster"
  type        = string
}

variable "SUBNETS" {
  description = "List of subnets for the ECS task"
  type        = list(string)
}

variable "SECURITY_GROUPS" {
  description = "List of security groups for the ECS task"
  type        = list(string)
}