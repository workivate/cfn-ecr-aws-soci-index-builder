# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os
import re

def handler(event, context):
    """
    Lambda function to parse repository names from filters and generate ECR repository ARNs.
    This function is used during Terraform planning to determine which ECR repositories
    the SOCI index generator Lambda needs access to.
    """
    
    try:
        filters = event.get('filters', [])
        aws_account_id = os.environ.get('AWS_ACCOUNT_ID')
        
        if not aws_account_id:
            raise ValueError("AWS_ACCOUNT_ID environment variable is required")
        
        repository_arns = []
        
        for filter_pattern in filters:
            # Split repository:tag pattern
            if ':' in filter_pattern:
                repo_pattern = filter_pattern.split(':')[0]
            else:
                repo_pattern = filter_pattern
            
            # Convert wildcard pattern to ECR repository ARN
            # For wildcard patterns, we need to grant access to all repositories
            if '*' in repo_pattern or repo_pattern == '':
                # Grant access to all ECR repositories in the account
                repository_arns.append(f"arn:aws:ecr:*:{aws_account_id}:repository/*")
            else:
                # Grant access to specific repository
                repository_arns.append(f"arn:aws:ecr:*:{aws_account_id}:repository/{repo_pattern}")
        
        # Remove duplicates
        repository_arns = list(set(repository_arns))
        
        # If no specific repositories and no wildcards, default to all repositories
        if not repository_arns:
            repository_arns = [f"arn:aws:ecr:*:{aws_account_id}:repository/*"]
        
        response_body = {
            "repository_arns": repository_arns
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps(response_body)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
