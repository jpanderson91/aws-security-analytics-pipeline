# Input Variables for Security Analytics Pipeline

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "security-analytics"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "owner" {
  description = "Owner of the resources"
  type        = string
  default     = "DevOps-Team"
}

variable "kinesis_shard_count" {
  description = "Number of shards for Kinesis stream"
  type        = number
  default     = 1
  
  validation {
    condition     = var.kinesis_shard_count >= 1 && var.kinesis_shard_count <= 1000
    error_message = "Kinesis shard count must be between 1 and 1000."
  }
}

variable "data_retention_days" {
  description = "Number of days to retain data in S3"
  type        = number
  default     = 2555  # 7 years for compliance
  
  validation {
    condition     = var.data_retention_days >= 1
    error_message = "Data retention days must be at least 1."
  }
}

variable "log_level" {
  description = "Log level for Lambda functions"
  type        = string
  default     = "INFO"
  
  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR"], var.log_level)
    error_message = "Log level must be one of: DEBUG, INFO, WARNING, ERROR."
  }
}

variable "alert_email" {
  description = "Email address for security alerts"
  type        = string
  default     = ""
}

variable "enable_guardduty" {
  description = "Whether to enable GuardDuty detector"
  type        = bool
  default     = true
}

variable "enable_cloudtrail" {
  description = "Whether to enable CloudTrail logging"
  type        = bool
  default     = true
}

variable "cloudwatch_log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 14
  
  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.cloudwatch_log_retention_days)
    error_message = "CloudWatch log retention days must be a valid retention period."
  }
}

variable "enable_s3_intelligent_tiering" {
  description = "Whether to enable S3 Intelligent Tiering for cost optimization"
  type        = bool
  default     = false
}

variable "lambda_memory_size" {
  description = "Memory size for Lambda functions (MB)"
  type        = number
  default     = 512
  
  validation {
    condition     = var.lambda_memory_size >= 128 && var.lambda_memory_size <= 10240
    error_message = "Lambda memory size must be between 128 and 10240 MB."
  }
}

variable "lambda_timeout" {
  description = "Timeout for Lambda functions (seconds)"
  type        = number
  default     = 300
  
  validation {
    condition     = var.lambda_timeout >= 1 && var.lambda_timeout <= 900
    error_message = "Lambda timeout must be between 1 and 900 seconds."
  }
}

variable "kinesis_retention_hours" {
  description = "Kinesis stream retention period in hours"
  type        = number
  default     = 24
  
  validation {
    condition     = var.kinesis_retention_hours >= 24 && var.kinesis_retention_hours <= 8760
    error_message = "Kinesis retention must be between 24 and 8760 hours."
  }
}

variable "enable_encryption" {
  description = "Whether to enable encryption for all resources"
  type        = bool
  default     = true
}

variable "cost_center" {
  description = "Cost center for billing allocation"
  type        = string
  default     = "Security"
}

variable "compliance_standard" {
  description = "Compliance standard to follow"
  type        = string
  default     = "SOC2"
  
  validation {
    condition     = contains(["SOC2", "PCI-DSS", "HIPAA", "ISO27001"], var.compliance_standard)
    error_message = "Compliance standard must be one of: SOC2, PCI-DSS, HIPAA, ISO27001."
  }
}

variable "backup_enabled" {
  description = "Whether to enable automated backups"
  type        = bool
  default     = true
}

variable "monitoring_enabled" {
  description = "Whether to enable detailed monitoring"
  type        = bool
  default     = true
}

variable "auto_scaling_enabled" {
  description = "Whether to enable auto-scaling for Kinesis"
  type        = bool
  default     = false
}

variable "custom_threat_lists" {
  description = "List of custom threat intelligence feeds"
  type        = list(string)
  default     = []
}

variable "allowed_source_ips" {
  description = "List of allowed source IP addresses for administration"
  type        = list(string)
  default     = []
}

variable "notification_endpoints" {
  description = "List of notification endpoints for alerts"
  type = list(object({
    protocol = string
    endpoint = string
  }))
  default = []
  
  validation {
    condition = alltrue([
      for endpoint in var.notification_endpoints :
      contains(["email", "sms", "slack", "teams"], endpoint.protocol)
    ])
    error_message = "Notification protocol must be one of: email, sms, slack, teams."
  }
}
