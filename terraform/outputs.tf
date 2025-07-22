# Output Values for Security Analytics Pipeline

# S3 Resources
output "security_data_lake_bucket_name" {
  description = "Name of the S3 bucket for security data lake"
  value       = aws_s3_bucket.security_data_lake.bucket
}

output "security_data_lake_bucket_arn" {
  description = "ARN of the S3 bucket for security data lake"
  value       = aws_s3_bucket.security_data_lake.arn
}

output "cloudtrail_logs_bucket_name" {
  description = "Name of the S3 bucket for CloudTrail logs"
  value       = aws_s3_bucket.cloudtrail_logs.bucket
}

# Kinesis Resources
output "kinesis_stream_name" {
  description = "Name of the Kinesis stream for security events"
  value       = aws_kinesis_stream.security_events.name
}

output "kinesis_stream_arn" {
  description = "ARN of the Kinesis stream for security events"
  value       = aws_kinesis_stream.security_events.arn
}

# Lambda Resources
output "lambda_function_name" {
  description = "Name of the Lambda function for event processing"
  value       = aws_lambda_function.event_processor.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function for event processing"
  value       = aws_lambda_function.event_processor.arn
}

# IAM Resources
output "lambda_execution_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_execution_role.arn
}

output "eventbridge_kinesis_role_arn" {
  description = "ARN of the EventBridge to Kinesis role"
  value       = aws_iam_role.eventbridge_kinesis_role.arn
}

# Security Resources
output "guardduty_detector_id" {
  description = "ID of the GuardDuty detector"
  value       = var.enable_guardduty ? aws_guardduty_detector.security_detector[0].id : null
}

output "cloudtrail_arn" {
  description = "ARN of the CloudTrail"
  value       = aws_cloudtrail.security_trail.arn
}

output "kms_key_id" {
  description = "ID of the KMS key for encryption"
  value       = aws_kms_key.security_analytics.key_id
}

output "kms_key_arn" {
  description = "ARN of the KMS key for encryption"
  value       = aws_kms_key.security_analytics.arn
}

# Monitoring Resources
output "sns_topic_arn" {
  description = "ARN of the SNS topic for security alerts"
  value       = aws_sns_topic.security_alerts.arn
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group for Lambda"
  value       = aws_cloudwatch_log_group.event_processor.name
}

# Glue Resources
output "glue_database_name" {
  description = "Name of the Glue database for security analytics"
  value       = aws_glue_catalog_database.security_analytics.name
}

output "glue_table_name" {
  description = "Name of the Glue table for security events"
  value       = aws_glue_catalog_table.security_events.name
}

# EventBridge Resources (conditional)
output "eventbridge_rule_name" {
  description = "Name of the EventBridge rule for GuardDuty findings"
  value       = var.enable_guardduty ? aws_cloudwatch_event_rule.guardduty_findings[0].name : null
}

output "eventbridge_rule_arn" {
  description = "ARN of the EventBridge rule for GuardDuty findings"
  value       = var.enable_guardduty ? aws_cloudwatch_event_rule.guardduty_findings[0].arn : null
}

# Configuration Outputs
output "aws_region" {
  description = "AWS region where resources are deployed"
  value       = var.aws_region
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "project_name" {
  description = "Project name"
  value       = var.project_name
}

# URLs and Endpoints
output "quicksight_dashboard_url" {
  description = "URL for QuickSight dashboard (to be created manually)"
  value       = "https://${var.aws_region}.quicksight.aws.amazon.com/sn/dashboards"
}

output "athena_query_console_url" {
  description = "URL for Athena query console"
  value       = "https://console.aws.amazon.com/athena/home?region=${var.aws_region}#query"
}

output "cloudwatch_dashboard_url" {
  description = "URL for CloudWatch dashboard"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:"
}

# Cost Tracking
output "resource_tags" {
  description = "Common tags applied to all resources"
  value = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
    Purpose     = "Security Analytics Pipeline"
  }
}

# Security Configuration
output "encryption_status" {
  description = "Encryption status for all resources"
  value = {
    s3_encryption     = "AES256"
    kinesis_encryption = "KMS"
    kms_key_id        = aws_kms_key.security_analytics.key_id
  }
}

# Data Pipeline Endpoints
output "data_pipeline_endpoints" {
  description = "Key endpoints for the data pipeline"
  value = {
    kinesis_stream = aws_kinesis_stream.security_events.name
    s3_data_lake   = aws_s3_bucket.security_data_lake.bucket
    glue_database  = aws_glue_catalog_database.security_analytics.name
    sns_alerts     = aws_sns_topic.security_alerts.arn
  }
}

# Athena Query Examples
output "sample_athena_queries" {
  description = "Sample Athena queries for security analysis"
  value = {
    top_events = "SELECT event_type, COUNT(*) as count FROM ${aws_glue_catalog_table.security_events.name} GROUP BY event_type ORDER BY count DESC LIMIT 10"
    recent_events = "SELECT * FROM ${aws_glue_catalog_table.security_events.name} WHERE event_time > current_timestamp - interval '24' hour"
    ip_analysis = "SELECT source_ip, COUNT(*) as activity_count FROM ${aws_glue_catalog_table.security_events.name} GROUP BY source_ip ORDER BY activity_count DESC"
  }
}

# Deployment Information
output "deployment_info" {
  description = "Information about the deployment"
  value = {
    deployed_at     = timestamp()
    terraform_version = "~> 1.0"
    aws_provider_version = "~> 5.0"
    resources_created = "15+ AWS resources"
  }
}
