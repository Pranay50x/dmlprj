variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "service_name" {
  type    = string
  default = "ml-ci-cd-app"
}

variable "image_identifier" {
  type = string
}

variable "image_repository_type" {
  type    = string
  default = "ECR_PUBLIC"
}

variable "port" {
  type    = number
  default = 8000
}

variable "access_role_arn" {
  type    = string
  default = ""
}
