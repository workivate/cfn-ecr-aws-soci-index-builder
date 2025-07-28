# SOCI ECR Index Generator - Terraform Module

This Terraform module implements AWS ECR SOCI (Seekable OCI) index generation functionality. SOCI is a solution that enables faster container image pulls by generating an index that allows Docker/containerd to download specific files without downloading the entire image layer, significantly improving container startup times.

## Architecture

The implementation consists of:

1. **S3 bucket** for storing Lambda deployment assets (automatically created)
2. **ECR Image Action Event Filter Lambda** - Filters ECR image push events based on repository/tag filters
3. **SOCI Index Generator Lambda** - Generates SOCI index for filtered container images
4. **EventBridge Rule** - Triggers the filter lambda when images are pushed to ECR
5. **IAM roles and policies** for the Lambda functions
6. **CloudWatch Log Groups** for Lambda logging

## Prerequisites

- **Terraform >= 1.0**: Infrastructure as Code tool
- **AWS CLI**: Configured with appropriate permissions
- **Ubuntu 24.04**: This module is designed for Ubuntu 24.04 systems
- **Sudo access**: Required for automatic dependency installation

**Note**: The Terraform configuration will automatically install all required dependencies on Ubuntu 24.04, including:
- Go 1.24 (if not present or insufficient version)
- Build tools (make, gcc, g++, git, zip)
- Development libraries (zlib1g-dev)
- Python3-pip

No manual dependency installation is required - the system will handle everything automatically during `terraform apply`.

## Required AWS Permissions

The AWS credentials used to deploy this module need the following permissions:

- S3: Create bucket, put/get objects, configure bucket policies
- Lambda: Create functions, update function code, manage permissions
- IAM: Create roles, policies, and attachments
- EventBridge: Create rules and targets
- CloudWatch: Create log groups
- ECR: Read repository information (for the Lambda functions)

## Usage

1. **Clone or download this module**

2. **Copy the example variables file:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

3. **Edit terraform.tfvars with your desired configuration:**
   ```hcl
   aws_region = "us-east-1"
   resource_prefix = "MyCompany"
   soci_repository_image_tag_filters = ["*:*"]
   ```

4. **Initialize Terraform:**
   ```bash
   terraform init
   ```

5. **Plan the deployment:**
   ```bash
   terraform plan
   ```

6. **Apply the configuration:**
   ```bash
   terraform apply
   ```

## Configuration Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `aws_region` | string | - | AWS region where resources will be created |
| `resource_prefix` | string | "Soci" | Prefix for AWS resource names |
| `soci_repository_image_tag_filters` | list(string) | ["*:*"] | Repository:tag filter patterns for SOCI index generation |
| `ecr_image_filter_lambda_handler` | string | "ecr_image_action_event_filtering_lambda_function.lambda_handler" | Handler for the ECR image filter Lambda |
| `ecr_image_filter_lambda_runtime` | string | "python3.10" | Runtime for the ECR image filter Lambda |
| `soci_index_generator_lambda_handler` | string | "main" | Handler for the SOCI index generator Lambda |
| `soci_index_generator_lambda_runtime` | string | "provided.al2" | Runtime for the SOCI index generator Lambda |
| `soci_ecr_image_filter_lambda_timeout` | number | 900 | Timeout in seconds for Lambda functions |
| `soci_index_generator_lambda_ephemeral_storage` | number | 10240 | Ephemeral storage in MB for SOCI generator Lambda |
| `soci_index_generator_lambda_memory_size` | number | 1024 | Memory in MB for SOCI generator Lambda |
| `soci_ecr_lambda_log_retention_days` | number | 14 | CloudWatch log retention in days |
| `soci_index_version` | string | "V2" | SOCI index version (V1 or V2) |

## Repository and Tag Filters

The `soci_repository_image_tag_filters` variable determines which ECR images will have SOCI indexes generated when pushed. Examples:

- `["*:*"]` - Generate SOCI index for all images in all repositories (default)
- `["app-repo:prod-*"]` - Only for images in 'app-repo' with tags starting with 'prod-'
- `["frontend:latest", "backend:v*"]` - For specific repository/tag combinations
- `["my-app:*", "another-app:v1.*"]` - Multiple patterns

## Outputs

| Output | Description |
|--------|-------------|
| `s3_bucket_name` | Name of the S3 bucket containing Lambda deployment assets |
| `s3_bucket_arn` | ARN of the S3 bucket containing Lambda deployment assets |
| `ecr_image_filter_lambda_arn` | ARN of the ECR Image Action Event Filter Lambda function |
| `soci_index_generator_lambda_arn` | ARN of the SOCI Index Generator Lambda function |
| `eventbridge_rule_arn` | ARN of the EventBridge rule that triggers the Lambda functions |

## How It Works

1. When a container image is pushed to ECR, EventBridge generates an "ECR Image Action" event
2. The EventBridge rule triggers the ECR Image Action Event Filter Lambda
3. The filter Lambda checks if the image matches any of the configured repository:tag filters
4. If there's a match, it invokes the SOCI Index Generator Lambda
5. The SOCI Index Generator Lambda:
   - Downloads the container image from ECR
   - Generates a SOCI index for the image
   - Uploads the SOCI index back to ECR (for V1) or creates a new tagged image (for V2)

## SOCI Index Versions

- **V1**: Creates a separate SOCI index artifact that's stored alongside the original image
- **V2**: Creates a new OCI image index that includes both the original image and SOCI artifacts, tagged with a "-soci" suffix

## Troubleshooting

### Lambda Build Issues

If the Go Lambda build fails:

1. Ensure Go 1.23+ is installed
2. Check that the `make` utility is available
3. Verify all Go dependencies are accessible

### Permission Issues

If you encounter permission errors:

1. Verify your AWS credentials have the required permissions
2. Check that the Lambda execution roles have proper ECR access
3. Ensure the S3 bucket policies allow Lambda access

### EventBridge Not Triggering

If the Lambda functions aren't being triggered:

1. Verify the EventBridge rule is enabled
2. Check that the rule pattern matches your ECR events
3. Ensure the Lambda permission allows EventBridge to invoke the function

## Cleanup

To destroy all resources created by this module:

```bash
terraform destroy
```

Note: This will delete the S3 bucket and all Lambda deployment assets.

## Contributing

When modifying this module:

1. Update the Lambda source code in the `functions/source/` directories
2. Test the changes locally if possible
3. Update documentation as needed
4. Ensure Terraform formatting: `terraform fmt`

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.
