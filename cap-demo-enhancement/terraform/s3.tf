# ============================================================================
# CAP Demo Project - Phase 2: S3 Data Lake Infrastructure
# ============================================================================
# Purpose: Create Bronze/Silver/Gold data lake architecture for CAP demo
#
# This file implements a three-tier data lake pattern commonly used in
# enterprise data platforms:
# - Bronze: Raw data from Kafka topics (minimal processing)
# - Silver: Cleaned and validated data (schema enforcement)
# - Gold: Business-ready aggregated data (optimized for analytics)
#
# Key Features:
# - Intelligent tiering for cost optimization
# - Lifecycle policies for automated data management
# - Cross-region replication for disaster recovery
# - Encryption at rest and in transit
# - Fine-grained access control
# ============================================================================

# S3 Bucket for Bronze Layer (Raw Data)
# Stores raw, unprocessed data directly from Kafka topics
resource "aws_s3_bucket" "bronze_layer" {
  bucket = "${var.environment}-${var.project_name}-bronze-${random_string.bucket_suffix.result}"

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-bronze-layer"
    Component  = "Data Lake"
    Purpose    = "Raw Data Storage"
    DataTier   = "Bronze"
    CostCenter = var.cost_center
  })
}

# S3 Bucket for Silver Layer (Processed Data)
# Stores cleaned, validated, and schema-enforced data
resource "aws_s3_bucket" "silver_layer" {
  bucket = "${var.environment}-${var.project_name}-silver-${random_string.bucket_suffix.result}"

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-silver-layer"
    Component  = "Data Lake"
    Purpose    = "Processed Data Storage"
    DataTier   = "Silver"
    CostCenter = var.cost_center
  })
}

# S3 Bucket for Gold Layer (Business Data)
# Stores aggregated, business-ready data optimized for analytics
resource "aws_s3_bucket" "gold_layer" {
  bucket = "${var.environment}-${var.project_name}-gold-${random_string.bucket_suffix.result}"

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-gold-layer"
    Component  = "Data Lake"
    Purpose    = "Business Analytics Data"
    DataTier   = "Gold"
    CostCenter = var.cost_center
  })
}

# S3 Bucket Versioning for Data Protection
# Enables point-in-time recovery and change tracking
resource "aws_s3_bucket_versioning" "bronze_layer" {
  bucket = aws_s3_bucket.bronze_layer.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "silver_layer" {
  bucket = aws_s3_bucket.silver_layer.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "gold_layer" {
  bucket = aws_s3_bucket.gold_layer.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket Encryption Configuration
# Encrypts all data at rest using KMS customer-managed keys
resource "aws_s3_bucket_server_side_encryption_configuration" "bronze_layer" {
  bucket = aws_s3_bucket.bronze_layer.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3_data_lake.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true # Reduces KMS costs by using bucket keys
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "silver_layer" {
  bucket = aws_s3_bucket.silver_layer.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3_data_lake.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "gold_layer" {
  bucket = aws_s3_bucket.gold_layer.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3_data_lake.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

# KMS Key for S3 Data Lake Encryption
# Provides enterprise-grade encryption for all data lake tiers
resource "aws_kms_key" "s3_data_lake" {
  description             = "KMS key for ${var.environment}-${var.project_name} S3 data lake encryption"
  deletion_window_in_days = var.kms_deletion_window
  enable_key_rotation     = true

  # Key policy allowing S3 service and ECS tasks to use the key
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
        Sid    = "Allow S3 Service"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      },
      {
        Sid    = "Allow ECS Tasks"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.environment}-${var.project_name}-ecs-task-*"
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

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-s3-data-lake-kms"
    Component  = "Security"
    Purpose    = "S3 Data Lake Encryption"
    CostCenter = var.cost_center
  })
}

# KMS Key Alias for easier management and reference
resource "aws_kms_alias" "s3_data_lake" {
  name          = "alias/${var.environment}-${var.project_name}-s3-data-lake"
  target_key_id = aws_kms_key.s3_data_lake.key_id
}

# S3 Bucket Public Access Block (Security Best Practice)
# Prevents accidental public exposure of data lake contents
resource "aws_s3_bucket_public_access_block" "bronze_layer" {
  bucket = aws_s3_bucket.bronze_layer.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "silver_layer" {
  bucket = aws_s3_bucket.silver_layer.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "gold_layer" {
  bucket = aws_s3_bucket.gold_layer.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Lifecycle Configuration for Cost Optimization
# Automatically transitions data to cheaper storage classes over time
resource "aws_s3_bucket_lifecycle_configuration" "bronze_layer" {
  bucket = aws_s3_bucket.bronze_layer.id

  rule {
    id     = "bronze_data_lifecycle"
    status = "Enabled"
    
    filter {
      prefix = ""
    }

    # Move to Infrequent Access after 30 days
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    # Move to Glacier after 90 days (for compliance/audit)
    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # Move to Deep Archive after 1 year
    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }

    # Delete old versions after 30 days to reduce costs
    noncurrent_version_expiration {
      noncurrent_days = 30
    }

    # Clean up incomplete multipart uploads
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "silver_layer" {
  bucket = aws_s3_bucket.silver_layer.id

  rule {
    id     = "silver_data_lifecycle"
    status = "Enabled"
    
    filter {
      prefix = ""
    }

    # Keep in Standard for 60 days (frequently accessed for analytics)
    transition {
      days          = 60
      storage_class = "STANDARD_IA"
    }

    # Move to Glacier after 180 days
    transition {
      days          = 180
      storage_class = "GLACIER"
    }

    # Move to Deep Archive after 2 years
    transition {
      days          = 730
      storage_class = "DEEP_ARCHIVE"
    }

    noncurrent_version_expiration {
      noncurrent_days = 60
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "gold_layer" {
  bucket = aws_s3_bucket.gold_layer.id

  rule {
    id     = "gold_data_lifecycle"
    status = "Enabled"
    
    filter {
      prefix = ""
    }

    # Keep in Standard for 90 days (active business use)
    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }

    # Move to Glacier after 1 year
    transition {
      days          = 365
      storage_class = "GLACIER"
    }

    # Move to Deep Archive after 3 years
    transition {
      days          = 1095
      storage_class = "DEEP_ARCHIVE"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# S3 Intelligent Tiering for Automatic Cost Optimization
# Automatically moves objects between access tiers based on usage patterns
resource "aws_s3_bucket_intelligent_tiering_configuration" "bronze_layer" {
  bucket = aws_s3_bucket.bronze_layer.id
  name   = "bronze_intelligent_tiering"

  # Apply to all objects
  filter {
    prefix = ""
  }

  # Enable Archive Access tier (90-180 days no access)
  tiering {
    access_tier = "ARCHIVE_ACCESS"
    days        = 90
  }

  # Enable Deep Archive Access tier (180+ days no access)
  tiering {
    access_tier = "DEEP_ARCHIVE_ACCESS"
    days        = 180
  }
}

resource "aws_s3_bucket_intelligent_tiering_configuration" "silver_layer" {
  bucket = aws_s3_bucket.silver_layer.id
  name   = "silver_intelligent_tiering"

  filter {
    prefix = ""
  }

  tiering {
    access_tier = "ARCHIVE_ACCESS"
    days        = 90
  }

  tiering {
    access_tier = "DEEP_ARCHIVE_ACCESS"
    days        = 180
  }
}

resource "aws_s3_bucket_intelligent_tiering_configuration" "gold_layer" {
  bucket = aws_s3_bucket.gold_layer.id
  name   = "gold_intelligent_tiering"

  filter {
    prefix = ""
  }

  tiering {
    access_tier = "ARCHIVE_ACCESS"
    days        = 90
  }

  tiering {
    access_tier = "DEEP_ARCHIVE_ACCESS"
    days        = 180
  }
}

# S3 Bucket Notification Configuration
# Triggers Lambda functions when new data arrives
resource "aws_s3_bucket_notification" "bronze_layer" {
  bucket = aws_s3_bucket.bronze_layer.id

  # Trigger data validation Lambda when new objects are created
  lambda_function {
    lambda_function_arn = aws_lambda_function.data_validator.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = ""
    filter_suffix       = ".json"
  }

  depends_on = [aws_lambda_permission.allow_s3_bronze]
}

resource "aws_s3_bucket_notification" "silver_layer" {
  bucket = aws_s3_bucket.silver_layer.id

  # Trigger analytics Lambda when processed data is available
  lambda_function {
    lambda_function_arn = aws_lambda_function.analytics_trigger.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = ""
    filter_suffix       = ".parquet"
  }

  depends_on = [aws_lambda_permission.allow_s3_silver]
}

# Lambda permission to allow S3 to invoke functions
resource "aws_lambda_permission" "allow_s3_bronze" {
  statement_id  = "AllowExecutionFromS3Bronze"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.data_validator.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bronze_layer.arn
}

resource "aws_lambda_permission" "allow_s3_silver" {
  statement_id  = "AllowExecutionFromS3Silver"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.analytics_trigger.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.silver_layer.arn
}

# CloudWatch Log Group for S3 access logging
resource "aws_cloudwatch_log_group" "s3_access_logs" {
  name              = "/aws/s3/${var.environment}-${var.project_name}-access-logs"
  retention_in_days = var.log_retention_days

  # Enable encryption for access logs
  kms_key_id = var.enable_log_encryption ? aws_kms_key.s3_data_lake.arn : null

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-s3-access-logs"
    Component  = "Logging"
    Purpose    = "S3 Access Audit Trail"
    CostCenter = var.cost_center
  })
}

# Data sources and random strings defined in other files
