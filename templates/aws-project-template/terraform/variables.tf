# Terraform Variables Template

# Core Project Variables
variable "project_name" {
  description = "Name of the project for resource naming and tagging"
  type        = string
  default     = "{{PROJECT_NAME}}"
  
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"
}

variable "owner" {
  description = "Owner of the resources for cost tracking and contact"
  type        = string
  default     = "{{OWNER_NAME}}"
}

variable "cost_center" {
  description = "Cost center for billing allocation"
  type        = string
  default     = "{{COST_CENTER}}"
}

# Project-Specific Variables
variable "{{PRIMARY_SERVICE_VAR}}" {
  description = "Configuration for {{PRIMARY_SERVICE}}"
  type = object({
    enabled        = bool
    {{SERVICE_CONFIG_VARS}}
  })
  default = {
    enabled        = true
    {{SERVICE_CONFIG_DEFAULTS}}
  }
}

variable "{{SECONDARY_SERVICE_VAR}}" {
  description = "Configuration for {{SECONDARY_SERVICE}}"
  type = object({
    enabled        = bool
    {{SERVICE_CONFIG_VARS_2}}
  })
  default = {
    enabled        = true
    {{SERVICE_CONFIG_DEFAULTS_2}}
  }
}

# Storage Configuration
variable "storage_config" {
  description = "Storage configuration settings"
  type = object({
    bucket_prefix     = string
    versioning       = bool
    encryption       = bool
    lifecycle_days   = number
  })
  default = {
    bucket_prefix    = "{{PROJECT_NAME}}"
    versioning      = true
    encryption      = true
    lifecycle_days  = 30
  }
}

# Monitoring and Logging
variable "monitoring_config" {
  description = "Monitoring and alerting configuration"
  type = object({
    enable_dashboards     = bool
    enable_alerts        = bool
    log_retention_days   = number
    metric_namespace     = string
  })
  default = {
    enable_dashboards    = true
    enable_alerts       = true
    log_retention_days  = 7
    metric_namespace    = "{{PROJECT_NAME}}/{{PRIMARY_SERVICE}}"
  }
}

# Security Configuration
variable "security_config" {
  description = "Security configuration settings"
  type = object({
    enable_encryption    = bool
    kms_key_rotation    = bool
    vpc_enabled         = bool
    public_access       = bool
  })
  default = {
    enable_encryption   = true
    kms_key_rotation   = true
    vpc_enabled        = false  # Set to true for enterprise deployment
    public_access      = false
  }
}

# Cost Optimization Variables
variable "cost_optimization" {
  description = "Cost optimization settings"
  type = object({
    auto_scaling        = bool
    spot_instances      = bool
    reserved_capacity   = bool
    budget_limit_usd    = number
  })
  default = {
    auto_scaling       = true
    spot_instances     = false  # Set to true for dev environments
    reserved_capacity  = false  # Set to true for prod environments
    budget_limit_usd   = {{BUDGET_LIMIT}}
  }
}

# Enterprise Features (disabled by default for cost optimization)
variable "enterprise_features" {
  description = "Enterprise features configuration"
  type = object({
    {{ENTERPRISE_FEATURE_1}}        = bool
    {{ENTERPRISE_FEATURE_2}}        = bool
    {{ENTERPRISE_FEATURE_3}}        = bool
    advanced_monitoring             = bool
  })
  default = {
    {{ENTERPRISE_FEATURE_1}}        = false
    {{ENTERPRISE_FEATURE_2}}        = false
    {{ENTERPRISE_FEATURE_3}}        = false
    advanced_monitoring             = false
  }
}

# Resource Sizing
variable "resource_sizing" {
  description = "Resource sizing configuration for different environments"
  type = object({
    {{PRIMARY_COMPUTE_SIZE}}    = string
    {{SECONDARY_COMPUTE_SIZE}}  = string
    storage_class              = string
    backup_retention           = number
  })
  default = {
    {{PRIMARY_COMPUTE_SIZE}}   = "{{DEFAULT_COMPUTE_SIZE}}"    # Cost-optimized default
    {{SECONDARY_COMPUTE_SIZE}} = "{{DEFAULT_COMPUTE_SIZE_2}}"  # Cost-optimized default
    storage_class             = "STANDARD_IA"                  # Cost-optimized storage
    backup_retention          = 7                             # Days
  }
}

# Tagging Configuration
variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {
    {{DEFAULT_TAGS}}
  }
}
