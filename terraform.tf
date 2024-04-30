
terraform {
  backend "s3" {
    bucket         = "s3statebackend0123123"
    dynamodb_table = "state-lock"
    key            = "global/mystatefile/terraform.tfstate"
    region         = "ap-southeast-1"
    encrypt        = true

  }
  required_version = "~> 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.7.0"
    }

  }
}
