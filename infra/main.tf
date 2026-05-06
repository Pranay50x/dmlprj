terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_apprunner_service" "app" {
  service_name = var.service_name

  source_configuration {
    image_repository {
      image_identifier      = var.image_identifier
      image_repository_type = var.image_repository_type

      image_configuration {
        port = var.port
      }
    }

    dynamic "authentication_configuration" {
      for_each = var.access_role_arn == "" ? [] : [1]
      content {
        access_role_arn = var.access_role_arn
      }
    }

    auto_deployments_enabled = true
  }
}
