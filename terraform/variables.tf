variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Project name used to prefix all resources"
  type        = string
  default     = "datascienceproject"
}

variable "task_cpu" {
  description = "Fargate task CPU units (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 512
}

variable "task_memory" {
  description = "Fargate task memory in MiB"
  type        = number
  default     = 1024
}

variable "desired_count" {
  description = "Number of ECS tasks to run"
  type        = number
  default     = 1
}

variable "mlflow_tracking_uri" {
  description = "MLflow/DagsHub tracking URI"
  type        = string
  default     = "https://dagshub.com/salimnextdev/datascienceproject.mlflow"
}

variable "mlflow_tracking_username" {
  description = "DagsHub username"
  type        = string
  default     = "salimnextdev"
}

variable "mlflow_tracking_password_secret_arn" {
  description = "ARN of the AWS Secrets Manager secret holding the DagsHub token (MLFLOW_TRACKING_PASSWORD)"
  type        = string
}
