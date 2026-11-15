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
    key            = "dev/terraform.tfstate"
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
  env                                 = "dev"
  aws_region                          = var.aws_region
  vpc_cidr                            = "10.0.0.0/16"
  task_cpu                            = 256
  task_memory                         = 512
  desired_count                       = 1
  log_retention_days                  = 3
  mlflow_tracking_uri                 = var.mlflow_tracking_uri
  mlflow_tracking_username            = var.mlflow_tracking_username
  mlflow_tracking_password_secret_arn = var.mlflow_tracking_password_secret_arn
}
