terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = ">= 5.0"
      configuration_aliases = [aws.peer1, aws.peer2, aws.peer3, aws.us-east-1] # The us-east-1 provider is needed AWS Cloudfront certs
    }
  }
}
