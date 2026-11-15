terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.6"

  backend "s3" {
    bucket         = "datascienceproject-tfstate"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "datascienceproject-tfstate-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}

module "app" {
  source = "../../modules/app"

  project                             = "datascienceproject"
  env                                 = "prod"
  aws_region                          = var.aws_region
  vpc_cidr                            = "10.2.0.0/16"
  task_cpu                            = 1024
  task_memory                         = 2048
  desired_count                       = 2
  log_retention_days                  = 30
  mlflow_tracking_uri                 = var.mlflow_tracking_uri
  mlflow_tracking_username            = var.mlflow_tracking_username
  mlflow_tracking_password_secret_arn = var.mlflow_tracking_password_secret_arn
  acm_certificate_arn                 = var.acm_certificate_arn
}