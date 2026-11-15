variable "project" {
  type = string
}

variable "env" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "task_cpu" {
  type = number
}

variable "task_memory" {
  type = number
}

variable "desired_count" {
  type = number
}

variable "log_retention_days" {
  type = number
}

variable "mlflow_tracking_uri" {
  type = string
}

variable "mlflow_tracking_username" {
  type = string
}

variable "mlflow_tracking_password_secret_arn" {
  type = string
}
