variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "mlflow_tracking_uri" {
  type    = string
  default = "https://dagshub.com/salimnextdev/datascienceproject.mlflow"
}

variable "mlflow_tracking_username" {
  type    = string
  default = "salimnextdev"
}

variable "mlflow_tracking_password_secret_arn" {
  type = string
}

variable "acm_certificate_arn" {
  type        = string
  description = "ARN of the ACM certificate for the HTTPS listener"
}
