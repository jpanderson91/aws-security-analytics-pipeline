# Terraform Outputs Template

# Core Infrastructure Outputs
output "aws_region" {
  description = "AWS region where resources are deployed"
  value       = data.aws_region.current.name
}

output "aws_account_id" {
  description = "AWS account ID where resources are deployed"
  value       = data.aws_caller_identity.current.account_id
  sensitive   = true
}

output "project_name" {
  description = "Project name used for resource naming"
  value       = var.project_name
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

# {{PRIMARY_SERVICE}} Outputs
output "{{PRIMARY_SERVICE_OUTPUT}}" {
  description = "{{PRIMARY_SERVICE}} configuration and endpoints"
  value = {
    {{PRIMARY_SERVICE_OUTPUT_DETAILS}}
  }
}

# {{SECONDARY_SERVICE}} Outputs
output "{{SECONDARY_SERVICE_OUTPUT}}" {
  description = "{{SECONDARY_SERVICE}} configuration and endpoints"
  value = {
    {{SECONDARY_SERVICE_OUTPUT_DETAILS}}
  }
}

# Storage Outputs
output "storage_resources" {
  description = "Storage resource information"
  value = {
    {{STORAGE_OUTPUT_DETAILS}}
  }
}

# Security Outputs
output "security_resources" {
  description = "Security and IAM resource information"
  value = {
    {{SECURITY_OUTPUT_DETAILS}}
  }
  sensitive = true
}

# Monitoring and Dashboard Outputs
output "monitoring_resources" {
  description = "Monitoring and dashboard information"
  value = {
    {{MONITORING_OUTPUT_DETAILS}}
  }
}

# URLs and Endpoints for Portfolio Demonstration
output "dashboard_urls" {
  description = "URLs for accessing dashboards and interfaces"
  value = {
    {{DASHBOARD_URL_OUTPUTS}}
  }
}

output "api_endpoints" {
  description = "API endpoints for testing and integration"
  value = {
    {{API_ENDPOINT_OUTPUTS}}
  }
}

# Cost and Resource Summary
output "deployment_summary" {
  description = "Summary of deployed resources and estimated costs"
  value = {
    total_resources     = {{RESOURCE_COUNT}}
    estimated_monthly_cost = "${{ESTIMATED_COST}}"
    deployment_region   = data.aws_region.current.name
    deployment_time     = timestamp()
    resource_summary = {
      {{RESOURCE_SUMMARY}}
    }
  }
}

# Testing and Validation Outputs
output "testing_information" {
  description = "Information for testing and validating the deployment"
  value = {
    {{TESTING_OUTPUT_DETAILS}}
  }
}

# Quick Commands for Portfolio Demonstration
output "portfolio_demo_commands" {
  description = "Commands to demonstrate the working system"
  value = {
    test_command        = "{{TEST_COMMAND}}"
    dashboard_command   = "{{DASHBOARD_COMMAND}}"
    monitoring_command  = "{{MONITORING_COMMAND}}"
    cleanup_command     = "terraform destroy -auto-approve"
  }
}

# Enterprise Features Status
output "enterprise_features_status" {
  description = "Status of enterprise features (enabled/disabled)"
  value = {
    {{ENTERPRISE_FEATURES_STATUS}}
  }
}

# Security Compliance Information
output "security_compliance" {
  description = "Security and compliance status"
  value = {
    encryption_enabled  = var.security_config.enable_encryption
    vpc_enabled        = var.security_config.vpc_enabled
    kms_rotation       = var.security_config.kms_key_rotation
    audit_logging      = true
    iam_least_privilege = true
  }
}
