# AWS Security Analytics Pipeline - Terraform Configuration

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      Owner       = var.owner
      Purpose     = "Security Analytics Pipeline"
    }
  }
}

# Data sources for existing resources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Local values for resource naming
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
  }
}

# S3 Bucket for data lake storage
resource "aws_s3_bucket" "security_data_lake" {
  bucket = "${local.name_prefix}-security-data-lake-${random_string.bucket_suffix.result}"
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket_versioning" "security_data_lake" {
  bucket = aws_s3_bucket.security_data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "security_data_lake" {
  bucket = aws_s3_bucket.security_data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 bucket lifecycle configuration (simplified for cost-optimized deployment)
# Note: Can be enhanced later with proper transition timing
resource "aws_s3_bucket_lifecycle_configuration" "security_data_lake" {
  bucket = aws_s3_bucket.security_data_lake.id

  rule {
    id     = "security_data_lifecycle"
    status = "Enabled"

    filter {
      prefix = "security-events/"
    }

    expiration {
      days = var.data_retention_days
    }
  }
}

# Kinesis Data Stream for real-time event processing
resource "aws_kinesis_stream" "security_events" {
  name             = "${local.name_prefix}-security-events"
  shard_count      = var.kinesis_shard_count
  retention_period = 24

  encryption_type = "KMS"
  kms_key_id      = aws_kms_key.security_analytics.arn

  shard_level_metrics = [
    "IncomingRecords",
    "OutgoingRecords",
  ]

  tags = local.common_tags
}

# KMS Key for encryption
resource "aws_kms_key" "security_analytics" {
  description             = "KMS key for Security Analytics Pipeline"
  deletion_window_in_days = 7

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow use of the key for Kinesis"
        Effect = "Allow"
        Principal = {
          Service = "kinesis.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_kms_alias" "security_analytics" {
  name          = "alias/${local.name_prefix}-security-analytics"
  target_key_id = aws_kms_key.security_analytics.key_id
}

# IAM Role for Lambda execution
resource "aws_iam_role" "lambda_execution_role" {
  name = "${local.name_prefix}-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

# IAM Policy for Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${local.name_prefix}-lambda-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "kinesis:DescribeStream",
          "kinesis:GetShardIterator",
          "kinesis:GetRecords",
          "kinesis:ListStreams"
        ]
        Resource = aws_kinesis_stream.security_events.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.security_data_lake.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.security_data_lake.arn
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = aws_kms_key.security_analytics.arn
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.security_alerts.arn
      }
    ]
  })
}

# Lambda function for processing security events
resource "aws_lambda_function" "event_processor" {
  filename         = "event_processor.zip"
  function_name    = "${local.name_prefix}-event-processor"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.11"
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size

  environment {
    variables = {
      S3_BUCKET_NAME      = aws_s3_bucket.security_data_lake.bucket
      KINESIS_STREAM_NAME = aws_kinesis_stream.security_events.name
      SNS_TOPIC_ARN       = aws_sns_topic.security_alerts.arn
      LOG_LEVEL          = var.log_level
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_cloudwatch_log_group.event_processor,
  ]

  tags = local.common_tags
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "event_processor" {
  name              = "/aws/lambda/${local.name_prefix}-event-processor"
  retention_in_days = var.cloudwatch_log_retention_days

  tags = local.common_tags
}

# Event source mapping for Kinesis to Lambda
resource "aws_lambda_event_source_mapping" "kinesis_lambda" {
  event_source_arn  = aws_kinesis_stream.security_events.arn
  function_name     = aws_lambda_function.event_processor.arn
  starting_position = "LATEST"
  batch_size        = 100
}

# CloudTrail for API logging
resource "aws_cloudtrail" "security_trail" {
  name           = "${local.name_prefix}-security-trail"
  s3_bucket_name = aws_s3_bucket.cloudtrail_logs.bucket

  event_selector {
    read_write_type                 = "All"
    include_management_events       = true
    exclude_management_event_sources = []

    data_resource {
      type   = "AWS::S3::Object"
      values = ["${aws_s3_bucket.security_data_lake.arn}/*"]
    }
  }

  depends_on = [aws_s3_bucket_policy.cloudtrail_logs]

  tags = local.common_tags
}

# S3 bucket for CloudTrail logs
resource "aws_s3_bucket" "cloudtrail_logs" {
  bucket = "${local.name_prefix}-cloudtrail-logs-${random_string.cloudtrail_suffix.result}"
}

resource "random_string" "cloudtrail_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket_policy" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail_logs.arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail_logs.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

# GuardDuty detector (optional for cost optimization)
resource "aws_guardduty_detector" "security_detector" {
  count  = var.enable_guardduty ? 1 : 0
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }

  tags = local.common_tags
}

# SNS topic for alerts
resource "aws_sns_topic" "security_alerts" {
  name = "${local.name_prefix}-security-alerts"

  tags = local.common_tags
}

# SNS topic subscription for email alerts
resource "aws_sns_topic_subscription" "security_alerts_email" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.security_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# Glue Database for data catalog
resource "aws_glue_catalog_database" "security_analytics" {
  name        = "${replace(local.name_prefix, "-", "_")}_security_analytics"
  description = "Database for Security Analytics Pipeline"
}

# Glue Table for security events
resource "aws_glue_catalog_table" "security_events" {
  name          = "security_events"
  database_name = aws_glue_catalog_database.security_analytics.name

  table_type = "EXTERNAL_TABLE"

  parameters = {
    "classification" = "parquet"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.security_data_lake.bucket}/security-events/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "event_time"
      type = "timestamp"
    }

    columns {
      name = "event_type"
      type = "string"
    }

    columns {
      name = "source_ip"
      type = "string"
    }

    columns {
      name = "user_identity"
      type = "string"
    }

    columns {
      name = "event_data"
      type = "string"
    }
  }
}

# EventBridge rule for GuardDuty findings (only if GuardDuty is enabled)
resource "aws_cloudwatch_event_rule" "guardduty_findings" {
  count       = var.enable_guardduty ? 1 : 0
  name        = "${local.name_prefix}-guardduty-findings"
  description = "Capture GuardDuty findings"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
  })

  tags = local.common_tags
}

# EventBridge target to Kinesis (only if GuardDuty is enabled)
resource "aws_cloudwatch_event_target" "kinesis_target" {
  count     = var.enable_guardduty ? 1 : 0
  rule      = aws_cloudwatch_event_rule.guardduty_findings[0].name
  target_id = "SendToKinesis"
  arn       = aws_kinesis_stream.security_events.arn

  kinesis_target {
    partition_key_path = "$.detail.id"
  }

  depends_on = [aws_iam_role.eventbridge_kinesis_role]
}

# IAM role for EventBridge to Kinesis
resource "aws_iam_role" "eventbridge_kinesis_role" {
  name = "${local.name_prefix}-eventbridge-kinesis-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy" "eventbridge_kinesis_policy" {
  name = "${local.name_prefix}-eventbridge-kinesis-policy"
  role = aws_iam_role.eventbridge_kinesis_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kinesis:PutRecord",
          "kinesis:PutRecords"
        ]
        Resource = aws_kinesis_stream.security_events.arn
      }
    ]
  })
}
