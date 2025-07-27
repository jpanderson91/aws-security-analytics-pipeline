# ============================================================================
# CAP Demo - Core Infrastructure Configuration
# ============================================================================
# Purpose: Terraform foundation for enterprise data ingestion platform
# Phase 1: MSK Kafka Foundation - Enterprise streaming architecture
# Date: July 25, 2025
# 
# This file establishes the core Terraform configuration including:
# - AWS provider with proper versioning for stability
# - Consistent resource tagging strategy for cost tracking
# - Multi-AZ data sources for high availability design
# - Naming conventions that scale across environments
# ============================================================================

# Terraform version constraints - ensures reproducible deployments
# Using Terraform 1.0+ for mature feature set and AWS Provider 5.0 for latest MSK features
terraform {
  required_version = ">= 1.0" # Minimum version for stable module support
  required_providers {
    aws = {
      source  = "hashicorp/aws" # Official AWS provider
      version = "~> 5.0"        # Version 5.x for latest MSK and VPC features
    }
  }
}

# AWS Provider configuration with enterprise-grade settings
# Uses environment variables for authentication (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
provider "aws" {
  region  = var.aws_region  # Configurable region (default: us-east-1 for MSK availability)
  # profile = var.aws_profile # Temporarily disabled to use environment variables

  # Default tags applied to ALL resources for consistent cost tracking and governance
  # These tags enable automated cost allocation, resource lifecycle management,
  # and compliance reporting across the entire infrastructure
  default_tags {
    tags = {
      Project     = "CAP-Demo"       # Project identifier for cost tracking
      Environment = var.environment  # Environment isolation (dev/staging/prod)
      Owner       = "CAP-Team"       # Ownership for accountability
      Purpose     = "Portfolio-Demo" # Business purpose classification
      CostCenter  = "Development"    # Financial allocation category
    }
  }
}

# ============================================================================
# Data Sources - External AWS Infrastructure Discovery
# ============================================================================

# Discover all available AZs in the selected region
# Critical for MSK deployment which requires multi-AZ for high availability
data "aws_availability_zones" "available" {
  state = "available" # Only include AZs that are currently operational
}

# Get current AWS account information for resource naming and security
# Used for generating unique resource names and IAM policy references
data "aws_caller_identity" "current" {}

# Random string for unique resource naming across all phases
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# ============================================================================
# Local Values - Computed Configuration and Naming Standards
# ============================================================================

# Centralized configuration values computed from variables and data sources
# This pattern ensures consistency across all resources and environments
locals {
  # Standardized naming prefix for all resources
  # Format: cap-demo-{environment} enables easy identification and cleanup
  name_prefix = "cap-demo-${var.environment}"

  # Common tags applied to all resources beyond the default provider tags
  # These supplement the provider default_tags for enhanced resource management
  common_tags = {
    Project     = "CAP-Demo"             # Consistent project identification
    Environment = var.environment        # Environment-specific tagging
    CreatedBy   = "Terraform"            # Infrastructure automation tracking
    Purpose     = "MSK-Kafka-Foundation" # Component-specific purpose
  }

  # Availability Zone selection for MSK cluster deployment
  # MSK requires exactly 3 AZs for optimal performance and fault tolerance
  # Using slice() ensures we get first 3 AZs regardless of region AZ count
  azs = slice(data.aws_availability_zones.available.names, 0, 3)
}
