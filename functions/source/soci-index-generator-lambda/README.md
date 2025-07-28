# SOCI Index Generator Lambda

This directory contains the Go-based AWS Lambda function that generates SOCI (Seekable OCI) indices for container images stored in Amazon ECR. The SOCI index enables faster container startup times by allowing lazy loading of container image layers.

## Overview

The SOCI Index Generator Lambda function:
- Listens to ECR image push events
- Downloads container images from ECR
- Generates SOCI indices for the images
- Pushes the SOCI indices back to ECR
- Supports both SOCI V1 and V2 index formats

## Prerequisites

Before building the Lambda function, ensure you have the following installed:
- Go 1.24.1 or later
- Make
- Git
- Python3 and pip
- GCC and G++ compilers
- Zlib development libraries

## Building the Lambda Function

### Automated Build Script

Use the provided build script to automatically install dependencies and build the Lambda function:

```bash
#!/bin/bash

set -euo pipefail

# ─── COLORS FOR LOGS ─────────────────────────────────────
GREEN='\033[0;32m'
BLUE='\033[1;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info()    { echo -e "${BLUE}ℹ $1${NC}"; }
log_success() { echo -e "${GREEN}✔ $1${NC}"; }
log_error()   { echo -e "${RED}✖ $1${NC}"; }
log_warn()    { echo -e "${YELLOW}⚠ $1${NC}"; }
log_step()    { echo -e "${GREEN}▶ $1${NC}"; }

# ─── INSTALL DEPENDENCIES ───────────────────────────────
log_step "Installing build tools..."
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends \
python3-pip \
make \
git \
zip \
gcc \
g++ \
zlib1g \
zlib1g-dev

# ─── INSTALL OR UPGRADE GO ──────────────────────────────
REQUIRED_GO_VERSION="1.24.1"
GO_DOWNLOAD_URL="https://go.dev/dl/go${REQUIRED_GO_VERSION}.linux-amd64.tar.gz"
GO_INSTALL_DIR="/usr/local"

version_ge() {
  [ "$(printf '%s\n' "$2" "$1" | sort -V | head -n1)" = "$2" ]
}

INSTALL_GO=false

if command -v go &>/dev/null; then
  INSTALLED_GO_VERSION=$(go version | awk '{print $3}' | sed 's/go//')
  log_info "Go is installed: version $INSTALLED_GO_VERSION"
  if ! version_ge "$INSTALLED_GO_VERSION" "$REQUIRED_GO_VERSION"; then
    log_info "Go version is outdated. Installing $REQUIRED_GO_VERSION..."
    INSTALL_GO=true
  fi
else
  log_info "Go is not installed. Installing $REQUIRED_GO_VERSION..."
  INSTALL_GO=true
fi

if [ "$INSTALL_GO" = true ]; then
  curl -fsSL "$GO_DOWNLOAD_URL" -o go${REQUIRED_GO_VERSION}.linux-amd64.tar.gz
  sudo rm -rf "$GO_INSTALL_DIR/go"
  sudo tar -C "$GO_INSTALL_DIR" -xzf go${REQUIRED_GO_VERSION}.linux-amd64.tar.gz
  rm go${REQUIRED_GO_VERSION}.linux-amd64.tar.gz
  log_success "Go $REQUIRED_GO_VERSION installed to $GO_INSTALL_DIR/go"
fi

export PATH=$PATH:/usr/local/go/bin
log_success "Final Go version: $(go version)"

# ─── BUILD GO LAMBDA ─────────────────────────────────────
log_info "📦 Building Go Lambda function..."
cd "$(dirname "$0")/../functions/source/soci-index-generator-lambda"

export GOPROXY=direct

log_info "🧹 Cleaning old build files..."
rm -f bootstrap soci_index_generator_lambda.zip

log_info "🔄 Downloading Go module dependencies..."
if ! go mod download > /dev/null 2>&1; then
  log_error "Failed to download Go module dependencies"
  log_warn  "Please check your internet connection or go.mod"
  exit 1
fi
log_success "Go module dependencies downloaded"

log_info "🛠 Building Go Lambda binary with Make..."
if ! make > /dev/null 2>&1; then
  log_error "Failed to build Go Lambda function"
  log_warn  "Check the Makefile output for build errors"
  exit 1
fi

if [ ! -f "soci_index_generator_lambda.zip" ]; then
  log_error "Expected output 'soci_index_generator_lambda.zip' not found"
  exit 1
fi

log_success "Go Lambda function built successfully"
log_success "Output: soci_index_generator_lambda.zip ✅"
```

### Manual Build Steps

If you prefer to build manually, follow these steps:

1. **Install Dependencies**:
   ```bash
   sudo apt-get update -y
   sudo apt-get install -y python3-pip make git zip gcc g++ zlib1g zlib1g-dev
   ```

2. **Install Go 1.24.1** (if not already installed):
   ```bash
   curl -fsSL "https://go.dev/dl/go1.24.1.linux-amd64.tar.gz" -o go1.24.1.linux-amd64.tar.gz
   sudo rm -rf /usr/local/go
   sudo tar -C /usr/local -xzf go1.24.1.linux-amd64.tar.gz
   export PATH=$PATH:/usr/local/go/bin
   ```

3. **Navigate to the Lambda directory**:
   ```bash
   cd functions/source/soci-index-generator-lambda
   ```

4. **Download Go dependencies**:
   ```bash
   go mod download
   ```

5. **Build the Lambda function**:
   ```bash
   make
   ```

## Build Output

The build process creates:
- `bootstrap`: The compiled Go binary for AWS Lambda
- `soci_index_generator_lambda.zip`: The deployment package containing the Lambda function

## Project Structure

```
soci-index-generator-lambda/
├── README.md                    # This file
├── go.mod                       # Go module definition
├── go.sum                       # Go module checksums
├── Makefile                     # Build configuration
├── Dockerfile                   # Container build configuration
├── handler.go                   # Main Lambda handler
├── handler_test.go              # Handler tests
├── bootstrap                    # Compiled binary (generated)
├── soci_index_generator_lambda.zip  # Deployment package (generated)
├── events/
│   └── ecr_image_action.go      # ECR event structures
└── utils/
    ├── fs/
    │   ├── fs.go                # Filesystem utilities
    │   └── fs_test.go           # Filesystem tests
    ├── log/
    │   └── log.go               # Logging utilities
    └── registry/
        ├── registry.go          # ECR registry utilities
        └── registry_test.go     # Registry tests
```

## Key Dependencies

The Lambda function uses the following major dependencies:
- **AWS Lambda Go SDK**: For Lambda runtime integration
- **AWS SDK for Go**: For ECR and other AWS service interactions
- **SOCI Snapshotter**: For generating SOCI indices
- **Containerd**: For container image manipulation
- **ORAS Go**: For OCI registry operations

## Environment Variables

The Lambda function supports the following environment variables:
- `soci_index_version`: Specifies the SOCI index version ("V1" or "V2")

## Testing

Run the test suite using the provided Makefile targets:

```bash
# Run unit tests (excludes integration tests)
make test

# Run integration tests (requires environment setup)
make test-integration

# Run all tests
make test-all
```

## Lambda Function Behavior

1. **Event Processing**: The function receives ECR image push events
2. **Validation**: Validates the incoming event structure and content
3. **Image Download**: Downloads the container image from ECR
4. **Index Generation**: Creates SOCI indices for the image layers
5. **Index Upload**: Pushes the generated indices back to ECR
6. **Cleanup**: Removes temporary files and artifacts

## SOCI Index Versions

- **V1**: Traditional SOCI index format
- **V2**: Enhanced OCI-compatible index format with tagging support

## Error Handling

The function handles various error scenarios:
- Invalid ECR events
- Network connectivity issues
- Insufficient storage space
- Image processing failures
- Registry authentication problems

## Performance Considerations

- The Lambda function is configured with a 15-minute timeout
- Temporary storage cleanup occurs 10 seconds before timeout
- Free space monitoring ensures adequate storage for large images
- Static linking ensures compatibility across different Lambda environments

## Deployment

The generated `soci_index_generator_lambda.zip` file can be deployed to AWS Lambda using:
- AWS CLI
- AWS Console
- Infrastructure as Code tools (CloudFormation, Terraform, CDK)

## Troubleshooting

Common issues and solutions:

1. **Build Failures**: Ensure all dependencies are installed and Go version is correct
2. **Memory Issues**: The Lambda may need increased memory allocation for large images
3. **Timeout Issues**: Consider increasing the Lambda timeout for very large images
4. **Permission Issues**: Ensure the Lambda execution role has appropriate ECR permissions
