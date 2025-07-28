# AWS SOCI Index Builder

This AWS solution automates the generation of Seekable OCI (SOCI) index artifacts and stores them in Amazon ECR. It provides an easy way for customers to try SOCI technology to lazily load container images.

## Overview

The AWS SOCI Index Builder solution consists of the following components:

1. **EventBridge Rule**: Triggers when an image is pushed to ECR
2. **ECR Image Action Event Filtering Lambda**: Filters ECR image push events based on repository and tag patterns
3. **SOCI Index Generator Lambda**: Generates SOCI index artifacts for the image and pushes them back to ECR

## SOCI Index Versions

The solution supports two versions of SOCI index:

- **V1**: The original SOCI index format based on the OCI referrers API
- **V2**: An improved format that attaches the SOCI index to an image directly

## Configuration Parameters

### SociRepositoryImageTagFilters

Comma-separated list of SOCI repository image tag filters. Each filter is a repository name followed by a colon, ":" and followed by a tag. Both repository names and tags may contain wildcards denoted by an asterisk, "*".

Examples:
- `prod*:latest`: Matches all images tagged with "latest" that are pushed to any repositories that start with "prod"
- `dev:*`: Matches all images pushed to the "dev" repository
- `*:*`: Matches all images pushed to all repositories in your private registry

### SociIndexVersion

The version of SOCI index to generate:
- `V1`: Original SOCI Index format
- `V2`: Latest SOCI Index format (Recommended)

### Taskcat Configuration

The solution uses taskcat for testing CloudFormation deployments across multiple regions. The `.taskcat.yml` file configurable options:

- **Regions**: List of AWS regions where you want to deploy the stack
- **SociRepositoryImageTagFilters**: Filter pattern for ECR repositories and image tags

Example configuration:
```yaml
regions:
  - us-east-1
  - us-west-2
  - eu-west-1

parameters:
  SociRepositoryImageTagFilters: "*:*"
```

## How It Works

1. When an image is pushed to ECR, an EventBridge rule triggers the ECR Image Action Event Filtering Lambda
2. The Lambda checks if the image matches the configured filters
3. If there's a match, it invokes the SOCI Index Generator Lambda
4. The SOCI Index Generator Lambda:
   - Pulls the image from ECR
   - Generates SOCI index artifacts using the specified version (V1 or V2)
   - Pushes the SOCI index artifacts back to ECR

## Terraform Deployment

This solution can be deployed using Terraform. The Terraform configuration provides a flexible and infrastructure-as-code approach to deploying the SOCI Index Builder.

### Prerequisites

- Terraform >= 1.0
- AWS CLI configured with appropriate permissions
- AWS Provider >= 5.0

### Required Variables

The following variable is required when deploying with Terraform:

| Variable | Type | Description |
|----------|------|-------------|
| `aws_region` | string | AWS region where the solution will be deployed |

### Optional Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `soci_repository_image_tag_filters` | list(string) | `["*:*"]` | List of repository:tag filter patterns for SOCI index generation |
| `resource_prefix` | string | `"Soci"` | Prefix for AWS resources created by the solution |
| `soci_index_version` | string | `"V2"` | Version of SOCI index to generate (V1 or V2) |
| `ecr_image_filter_lambda_handler` | string | `"ecr_image_action_event_filtering_lambda_function.lambda_handler"` | Handler function for ECR image filter Lambda |
| `ecr_image_filter_lambda_runtime` | string | `"python3.10"` | Runtime for ECR image filter Lambda |
| `soci_index_generator_lambda_handler` | string | `"main"` | Handler function for SOCI index generator Lambda |
| `soci_index_generator_lambda_runtime` | string | `"provided.al2"` | Runtime for SOCI index generator Lambda |
| `soci_ecr_lambda_log_retention_days` | number | `14` | CloudWatch log retention days for Lambda functions |
| `soci_ecr_image_filter_lambda_timeout` | number | `900` | Timeout in seconds for ECR image filter Lambda |
| `soci_index_generator_lambda_ephemeral_storage` | number | `10240` | Ephemeral storage size in MB for SOCI index generator Lambda |
| `soci_index_generator_lambda_memory_size` | number | `1024` | Memory size in MB for SOCI index generator Lambda |

### Usage Example

Create a `terraform.tfvars` file:

```hcl
aws_region = "us-east-1"
soci_repository_image_tag_filters = ["prod*:latest", "staging:*"]
resource_prefix = "MyApp"
soci_index_version = "V2"
```

Or create a `main.tf` file:

```hcl
module "soci_index_builder" {
  source = "./path/to/soci-index-builder"

  aws_region = "us-east-1"
  soci_repository_image_tag_filters = ["prod*:latest", "staging:*"]
  resource_prefix = "MyApp"
  soci_index_version = "V2"
}
```

### Deployment Commands

```bash
# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Apply the configuration
terraform apply

# Destroy the infrastructure (when needed)
terraform destroy
```

### Filter Pattern Examples

The `soci_repository_image_tag_filters` variable supports wildcard patterns:

- `["*:*"]` - Generate SOCI index for all images in all repositories (default)
- `["app-repo:prod-*"]` - Only for images in 'app-repo' with tags starting with 'prod-'
- `["frontend:latest", "backend:v*"]` - For specific repository/tag combinations
- `["prod*:latest"]` - All repositories starting with 'prod' and tagged 'latest'
- `["dev:*"]` - All images in the 'dev' repository regardless of tag

### AWS Resources Created

The Terraform configuration creates the following AWS resources:

- **Lambda Functions**: ECR Image Action Event Filter, SOCI Index Generator, Repository Name Parser
- **IAM Roles and Policies**: For Lambda execution and ECR access
- **EventBridge Rule**: To trigger on ECR image push events
- **CloudWatch Log Groups**: For Lambda function logging

### Provider Configuration

The solution requires the AWS provider with the following configuration:

```hcl
terraform {
  required_version = ">= 1.0"
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
```
