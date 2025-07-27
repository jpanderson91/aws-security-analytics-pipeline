# ============================================================================
# CAP Demo - Variable Definitions and Configuration Management
# ============================================================================
# Purpose: Centralized configuration management for enterprise demo environment
#
# This file defines all configurable parameters for the complete CAP demo
# infrastructure across all phases (MSK, ECS, Lambda, S3, Analytics).
# Variables are organized by functional area for maintainability.
#
# Design Principles:
# - Cost optimization through sensible defaults
# - Environment flexibility through validation
# - Security-first configuration options
# - Enterprise scalability patterns
# ============================================================================

# ============================================================================
# Project Configuration
# ============================================================================

variable "project_name" {
  description = "Project name for resource naming and tagging"
  type        = string
  default     = "cap-demo"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must only contain lowercase letters, numbers, and hyphens."
  }
}

variable "cost_center" {
  description = "Cost center for billing and resource allocation tracking"
  type        = string
  default     = "engineering-demo"
}

variable "common_tags" {
  description = "Common tags applied to all resources for cost tracking and management"
  type        = map(string)
  default = {
    Project      = "cap-demo"
    Environment  = "dev"
    ManagedBy    = "terraform"
    Owner        = "cap-team"
    Purpose      = "enterprise-interview-demo"
    CostCategory = "demo-infrastructure"
  }
}

# ============================================================================
# AWS Environment Configuration
# ============================================================================

variable "aws_region" {
  description = "AWS region for CAP demo infrastructure deployment"
  type        = string
  default     = "us-east-1" # MSK has best availability and pricing in us-east-1

  # Note: us-east-1 chosen for:
  # - Complete MSK feature availability
  # - Lower data transfer costs for demo
  # - Maximum AZ availability (6 AZs)
}

variable "aws_profile" {
  description = "AWS CLI profile to use for authentication and deployment"
  type        = string
  default     = "cap-demo" # Isolated profile prevents accidental deployments to wrong account

  # Using named profiles provides:
  # - Environment isolation
  # - Credential security
  # - Multi-account support
}

variable "environment" {
  description = "Environment name for resource tagging and naming conventions"
  type        = string
  default     = "dev"

  # Validation ensures only valid environment names are used
  # This prevents typos that could lead to resource naming conflicts
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

# ============================================================================
# MSK Kafka Cluster Configuration
# ============================================================================

variable "kafka_version" {
  description = "Apache Kafka version for MSK cluster - impacts feature availability"
  type        = string
  default     = "2.8.1" # Stable version with good MSK integration

  # Version 2.8.1 chosen for:
  # - Proven stability in MSK environment
  # - Full feature compatibility
  # - Balance between features and maturity
}

variable "kafka_instance_type" {
  description = "EC2 instance type for MSK broker nodes - affects performance and cost"
  type        = string
  default     = "kafka.t3.small" # Cost-optimized for demo, production would use kafka.m5.large+

  # t3.small provides:
  # - 2 vCPUs, 2GB RAM per broker
  # - Burstable performance suitable for demo workloads
  # - ~$45/month per broker vs ~$150/month for m5.large
}

variable "kafka_num_brokers" {
  description = "Number of Kafka brokers per availability zone (total = num_brokers * 3 AZs)"
  type        = number
  default     = 1 # 3 total brokers (1 per AZ) for demo cost control

  # Production considerations:
  # - 2+ brokers per AZ for high availability
  # - Odd numbers prevent split-brain scenarios
  # - More brokers = higher throughput but increased cost
}

variable "kafka_ebs_volume_size" {
  description = "EBS volume size per broker in GB - affects storage capacity and IOPS"
  type        = number
  default     = 100 # Minimal storage for demo, production typically 1TB+

  # 100GB provides:
  # - Sufficient space for demo topics and retention
  # - ~$10/month storage cost vs $100+/month for production
  # - Can be increased without cluster restart if needed
}

# ============================================================================
# Network Configuration
# ============================================================================

variable "vpc_cidr" {
  description = "CIDR block for VPC - defines available IP address space"
  type        = string
  default     = "10.0.0.0/16" # Provides 65,536 IP addresses

  # 10.0.0.0/16 chosen for:
  # - RFC 1918 private address space
  # - Large enough for future expansion
  # - Standard enterprise pattern
  # - No conflicts with common corporate networks
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames in VPC for easier MSK broker discovery"
  type        = bool
  default     = true # Required for MSK bootstrap broker hostname resolution
}

variable "enable_dns_support" {
  description = "Enable DNS support in VPC for internal name resolution"
  type        = bool
  default     = true # Required for MSK and other AWS service integration
}

# ============================================================================
# Security Configuration
# ============================================================================

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access MSK cluster - restricts network access"
  type        = list(string)
  default     = ["10.0.0.0/16"] # Only allow access from within VPC

  # Security best practice:
  # - Restrict to VPC CIDR only
  # - No public internet access (0.0.0.0/0)
  # - Additional CIDRs can be added for VPN/peering
}

variable "enable_logging" {
  description = "Enable MSK logging to CloudWatch for monitoring and troubleshooting"
  type        = bool
  default     = true # Essential for production operations and debugging

  # CloudWatch logging provides:
  # - Centralized log aggregation
  # - Real-time monitoring capabilities
  # - Integration with AWS alerting
}

# ============================================================================
# Cost Control Configuration
# ============================================================================

variable "enable_monitoring" {
  description = "Enable enhanced monitoring for MSK (JMX and OS metrics)"
  type        = bool
  default     = false # Disabled for demo cost control (~$0.50/hour savings)

  # Enhanced monitoring provides:
  # - Detailed broker metrics
  # - JMX monitoring data
  # - OS-level metrics
  # - Cost: ~$1.50/hour for 3-broker cluster
}

variable "enable_prometheus" {
  description = "Enable Prometheus monitoring integration for MSK"
  type        = bool
  default     = false # Disabled for demo cost control

  # Prometheus monitoring enables:
  # - Time-series metrics collection
  # - Integration with Grafana dashboards
  # - Custom alerting rules
  # - Additional cost and complexity
}

# ============================================================================
# Phase 2: ECS Container Orchestration Configuration
# ============================================================================

variable "enable_container_insights" {
  description = "Enable CloudWatch Container Insights for ECS cluster monitoring"
  type        = bool
  default     = true # Enables detailed container metrics and performance insights
}

variable "enable_access_logs" {
  description = "Enable ALB access logs for debugging and compliance"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention period for ECS task logs"
  type        = number
  default     = 14 # 2 weeks retention for demo - adjust for production

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.log_retention_days)
    error_message = "Log retention days must be a valid CloudWatch Logs retention value."
  }
}

variable "enable_log_encryption" {
  description = "Enable KMS encryption for CloudWatch logs"
  type        = bool
  default     = true # Enterprise security requirement
}

variable "kms_deletion_window" {
  description = "KMS key deletion window in days"
  type        = number
  default     = 7 # Minimum deletion window for demo environments

  validation {
    condition     = var.kms_deletion_window >= 7 && var.kms_deletion_window <= 30
    error_message = "KMS deletion window must be between 7 and 30 days."
  }
}

# Container Image Configuration
variable "security_processor_image" {
  description = "Docker image for security event processor"
  type        = string
  default     = "public.ecr.aws/docker/library/nginx:latest" # Placeholder - replace with actual image
}

variable "metrics_processor_image" {
  description = "Docker image for application metrics processor"
  type        = string
  default     = "public.ecr.aws/docker/library/nginx:latest" # Placeholder - replace with actual image
}

variable "workflow_processor_image" {
  description = "Docker image for customer workflow processor"
  type        = string
  default     = "public.ecr.aws/docker/library/nginx:latest" # Placeholder - replace with actual image
}

# ECS Task Resource Configuration
variable "security_processor_cpu" {
  description = "CPU units for security processor (1024 = 1 vCPU)"
  type        = number
  default     = 512 # 0.5 vCPU for demo workloads
}

variable "security_processor_memory" {
  description = "Memory in MB for security processor"
  type        = number
  default     = 1024 # 1GB memory
}

variable "metrics_processor_cpu" {
  description = "CPU units for metrics processor (1024 = 1 vCPU)"
  type        = number
  default     = 512 # 0.5 vCPU for demo workloads
}

variable "metrics_processor_memory" {
  description = "Memory in MB for metrics processor"
  type        = number
  default     = 1024 # 1GB memory
}

variable "workflow_processor_cpu" {
  description = "CPU units for workflow processor (1024 = 1 vCPU)"
  type        = number
  default     = 256 # 0.25 vCPU for light workflow tasks
}

variable "workflow_processor_memory" {
  description = "Memory in MB for workflow processor"
  type        = number
  default     = 512 # 512MB memory
}

# ECS Service Scaling Configuration
variable "security_processor_desired_count" {
  description = "Desired number of security processor tasks"
  type        = number
  default     = 2 # High availability with 2 tasks
}

variable "security_processor_min_capacity" {
  description = "Minimum number of security processor tasks"
  type        = number
  default     = 1
}

variable "security_processor_max_capacity" {
  description = "Maximum number of security processor tasks"
  type        = number
  default     = 5 # Can scale up to handle load spikes
}

variable "metrics_processor_desired_count" {
  description = "Desired number of metrics processor tasks"
  type        = number
  default     = 2
}

variable "metrics_processor_min_capacity" {
  description = "Minimum number of metrics processor tasks"
  type        = number
  default     = 1
}

variable "metrics_processor_max_capacity" {
  description = "Maximum number of metrics processor tasks"
  type        = number
  default     = 4
}

variable "workflow_processor_desired_count" {
  description = "Desired number of workflow processor tasks"
  type        = number
  default     = 1
}

variable "workflow_processor_min_capacity" {
  description = "Minimum number of workflow processor tasks"
  type        = number
  default     = 1
}

variable "workflow_processor_max_capacity" {
  description = "Maximum number of workflow processor tasks"
  type        = number
  default     = 3
}

# Data Integration Configuration
variable "kafka_bootstrap_servers" {
  description = "Kafka bootstrap servers for ECS tasks to connect to MSK"
  type        = string
  default     = "" # Will be populated from Phase 1 MSK outputs
}

variable "s3_data_bucket" {
  description = "S3 bucket for data lake storage"
  type        = string
  default     = "" # Will be populated from S3 data lake configuration
}

# Network Configuration (imported from Phase 1)
variable "vpc_id" {
  description = "VPC ID from Phase 1 network infrastructure"
  type        = string
  default     = "" # Will be populated from network.tf outputs
}

# Note: vpc_cidr variable already defined above

variable "private_subnet_ids" {
  description = "Private subnet IDs for ECS and Lambda deployment"
  type        = list(string)
  default     = [] # Will be populated from network.tf outputs
}

# ============================================================================
# Phase 2: Lambda Functions Configuration
# ============================================================================

variable "slack_webhook_url" {
  description = "Slack webhook URL for customer notifications (optional)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "alert_email" {
  description = "Email address for SNS alert notifications"
  type        = string
  default     = ""

  validation {
    condition     = var.alert_email == "" || can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.alert_email))
    error_message = "Alert email must be a valid email address or empty string."
  }
}

# ============================================================================
# Demo and Customer Scenario Configuration
# ============================================================================

variable "demo_customer_prefix" {
  description = "Prefix for demo customer resources and topic naming"
  type        = string
  default     = "customer"

  # Used for:
  # - Consistent customer resource naming
  # - Topic organization and identification
  # - Demo scenario scripting
}

variable "demo_topics" {
  description = "List of Kafka topics to create for CAP demo scenarios"
  type        = list(string)
  default = [
    "customer-events",     # General customer activity and user actions
    "security-logs",       # Security events, firewall logs, IDS alerts
    "application-metrics", # Application performance and health metrics
    "audit-trails",        # Compliance and audit logging
    "windows-events",      # Windows system events and event logs
    "database-logs"        # Database activity, queries, and connections
  ]

  # Topics represent real Toyota CAP scenarios:
  # - customer-events: User login attempts, application interactions
  # - security-logs: Security incident data, threat detection
  # - application-metrics: Performance monitoring, error tracking
  # - audit-trails: Compliance logging, data access tracking
  # - windows-events: System monitoring, event viewer data
  # - database-logs: Database performance, query analysis
}
