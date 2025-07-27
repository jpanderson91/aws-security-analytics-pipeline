# Terraform Configuration Template

# Provider configuration
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# AWS Provider
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project            = var.project_name
      Environment        = var.environment
      ManagedBy          = "Terraform"
      Owner              = var.owner
      CostCenter         = var.cost_center
      Purpose            = "{{PROJECT_PURPOSE}}"
      PortfolioProject   = "true"
      CreatedDate        = formatdate("YYYY-MM-DD", timestamp())
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Random suffix for globally unique resources
resource "random_id" "suffix" {
  byte_length = 4
}

# Local values for consistent naming
locals {
  # Naming convention: {project}-{environment}-{service}-{random}
  name_prefix = "${var.project_name}-${var.environment}"

  # Resource names with random suffix for global uniqueness
  bucket_name    = "${local.name_prefix}-{{PRIMARY_STORAGE}}-${random_id.suffix.hex}"
  lambda_prefix  = "${local.name_prefix}-{{PRIMARY_COMPUTE}}"

  # Common tags for all resources
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = var.owner
    CostCenter  = var.cost_center
  }
}

# {{PRIMARY_SERVICE}} Configuration
{{TERRAFORM_PRIMARY_SERVICE}}

# {{SECONDARY_SERVICE}} Configuration
{{TERRAFORM_SECONDARY_SERVICE}}

# {{STORAGE_SERVICE}} Configuration
{{TERRAFORM_STORAGE_SERVICE}}

# {{MONITORING_SERVICE}} Configuration
{{TERRAFORM_MONITORING_SERVICE}}

# Security and IAM Configuration
{{TERRAFORM_SECURITY_CONFIG}}

# Outputs for integration and validation
{{TERRAFORM_OUTPUTS}}
