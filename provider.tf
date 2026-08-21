terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.61.0"
    }
    klayers = {
      source  = "ldcorentin/klayer"
      version = "~> 1.0.0"
    }
  }
}

provider "aws" {
  # Configuration options
  region = "us-east-1"
}