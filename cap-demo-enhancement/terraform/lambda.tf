# ============================================================================
# CAP Demo Project - Phase 2: Lambda Functions for Event Processing
# ============================================================================
# Purpose: Deploy serverless functions for real-time data processing
#
# This file creates Lambda functions that provide event-driven processing
# capabilities for the CAP demo platform:
# - Data validation and quality checks
# - Real-time analytics and anomaly detection  
# - Customer notifications and alerting
# - Workflow automation and orchestration
#
# Key Features:
# - Serverless architecture for cost efficiency
# - Event-driven triggers from S3, MSK, and CloudWatch
# - Dead letter queues for error handling
# - VPC integration for secure data access
# - Environment variable configuration management
# ============================================================================

# ============================================================================
# Data Validation Lambda Function
# ============================================================================

# Data Validator Lambda Function
# Validates incoming data from S3 Bronze layer for schema compliance
resource "aws_lambda_function" "data_validator" {
  filename      = data.archive_file.data_validator.output_path
  function_name = "${var.environment}-${var.project_name}-data-validator"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 60
  memory_size   = 256

  source_code_hash = data.archive_file.data_validator.output_base64sha256

  # VPC configuration for secure access to MSK and other resources
  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [aws_security_group.lambda_functions.id]
  }

  # Environment variables for configuration
  environment {
    variables = {
      BRONZE_BUCKET = aws_s3_bucket.bronze_layer.bucket
      SILVER_BUCKET = aws_s3_bucket.silver_layer.bucket
      DLQ_URL       = aws_sqs_queue.data_validator_dlq.url
      LOG_LEVEL     = "INFO"
      ENVIRONMENT   = var.environment
      KMS_KEY_ID    = aws_kms_key.s3_data_lake.key_id
    }
  }

  # Dead letter queue for failed invocations
  dead_letter_config {
    target_arn = aws_sqs_queue.data_validator_dlq.arn
  }

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-data-validator"
    Component  = "Lambda"
    Purpose    = "Data Quality Validation"
    CostCenter = var.cost_center
  })

  depends_on = [
    aws_iam_role_policy_attachment.lambda_execution_policy,
    aws_cloudwatch_log_group.lambda_data_validator,
  ]
}

# Lambda function source code archive for data validator
data "archive_file" "data_validator" {
  type        = "zip"
  output_path = "${path.module}/lambda_packages/data_validator.zip"

  source {
    content = templatefile("${path.module}/lambda_functions/data_validator.py", {
      bronze_bucket = "BRONZE_BUCKET_PLACEHOLDER"
      silver_bucket = "SILVER_BUCKET_PLACEHOLDER"
    })
    filename = "lambda_function.py"
  }
}

# CloudWatch Log Group for Data Validator
resource "aws_cloudwatch_log_group" "lambda_data_validator" {
  name              = "/aws/lambda/${var.environment}-${var.project_name}-data-validator"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.enable_log_encryption ? aws_kms_key.s3_data_lake.arn : null

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-data-validator-logs"
    Component  = "Logging"
    Purpose    = "Lambda Function Logs"
    CostCenter = var.cost_center
  })
}

# Dead Letter Queue for Data Validator
resource "aws_sqs_queue" "data_validator_dlq" {
  name                      = "${var.environment}-${var.project_name}-data-validator-dlq"
  message_retention_seconds = 1209600 # 14 days

  # Enable encryption for sensitive data
  kms_master_key_id = aws_kms_key.s3_data_lake.key_id

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-data-validator-dlq"
    Component  = "Messaging"
    Purpose    = "Lambda Error Handling"
    CostCenter = var.cost_center
  })
}

# ============================================================================
# Analytics Trigger Lambda Function
# ============================================================================

# Analytics Trigger Lambda Function
# Processes data in Silver layer and generates business insights
resource "aws_lambda_function" "analytics_trigger" {
  filename      = data.archive_file.analytics_trigger.output_path
  function_name = "${var.environment}-${var.project_name}-analytics-trigger"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 300 # 5 minutes for analytics processing
  memory_size   = 512 # More memory for data processing

  source_code_hash = data.archive_file.analytics_trigger.output_base64sha256

  # VPC configuration
  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [aws_security_group.lambda_functions.id]
  }

  # Environment variables
  environment {
    variables = {
      SILVER_BUCKET = aws_s3_bucket.silver_layer.bucket
      GOLD_BUCKET   = aws_s3_bucket.gold_layer.bucket
      DLQ_URL       = aws_sqs_queue.analytics_trigger_dlq.url
      LOG_LEVEL     = "INFO"
      ENVIRONMENT   = var.environment
      KMS_KEY_ID    = aws_kms_key.s3_data_lake.key_id
    }
  }

  # Dead letter queue
  dead_letter_config {
    target_arn = aws_sqs_queue.analytics_trigger_dlq.arn
  }

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-analytics-trigger"
    Component  = "Lambda"
    Purpose    = "Real-time Analytics"
    CostCenter = var.cost_center
  })

  depends_on = [
    aws_iam_role_policy_attachment.lambda_execution_policy,
    aws_cloudwatch_log_group.lambda_analytics_trigger,
  ]
}

# Lambda function source code archive for analytics trigger
data "archive_file" "analytics_trigger" {
  type        = "zip"
  output_path = "${path.module}/lambda_packages/analytics_trigger.zip"

  source {
    content = templatefile("${path.module}/lambda_functions/analytics_trigger.py", {
      silver_bucket = "SILVER_BUCKET_PLACEHOLDER"
      gold_bucket   = "GOLD_BUCKET_PLACEHOLDER"
    })
    filename = "lambda_function.py"
  }
}

# CloudWatch Log Group for Analytics Trigger
resource "aws_cloudwatch_log_group" "lambda_analytics_trigger" {
  name              = "/aws/lambda/${var.environment}-${var.project_name}-analytics-trigger"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.enable_log_encryption ? aws_kms_key.s3_data_lake.arn : null

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-analytics-trigger-logs"
    Component  = "Logging"
    Purpose    = "Lambda Function Logs"
    CostCenter = var.cost_center
  })
}

# Dead Letter Queue for Analytics Trigger
resource "aws_sqs_queue" "analytics_trigger_dlq" {
  name                      = "${var.environment}-${var.project_name}-analytics-trigger-dlq"
  message_retention_seconds = 1209600 # 14 days
  kms_master_key_id         = aws_kms_key.s3_data_lake.key_id

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-analytics-trigger-dlq"
    Component  = "Messaging"
    Purpose    = "Lambda Error Handling"
    CostCenter = var.cost_center
  })
}

# ============================================================================
# Customer Notification Lambda Function
# ============================================================================

# Customer Notification Lambda Function
# Handles alerts, notifications, and customer communications
resource "aws_lambda_function" "customer_notifier" {
  filename      = data.archive_file.customer_notifier.output_path
  function_name = "${var.environment}-${var.project_name}-customer-notifier"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 60
  memory_size   = 256

  source_code_hash = data.archive_file.customer_notifier.output_base64sha256

  # VPC configuration
  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [aws_security_group.lambda_functions.id]
  }

  # Environment variables
  environment {
    variables = {
      SNS_TOPIC_ARN     = aws_sns_topic.customer_alerts.arn
      DLQ_URL           = aws_sqs_queue.customer_notifier_dlq.url
      LOG_LEVEL         = "INFO"
      ENVIRONMENT       = var.environment
      SLACK_WEBHOOK_URL = var.slack_webhook_url
    }
  }

  # Dead letter queue
  dead_letter_config {
    target_arn = aws_sqs_queue.customer_notifier_dlq.arn
  }

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-customer-notifier"
    Component  = "Lambda"
    Purpose    = "Customer Notifications"
    CostCenter = var.cost_center
  })

  depends_on = [
    aws_iam_role_policy_attachment.lambda_execution_policy,
    aws_cloudwatch_log_group.lambda_customer_notifier,
  ]
}

# Lambda function source code archive for customer notifier
data "archive_file" "customer_notifier" {
  type        = "zip"
  output_path = "${path.module}/lambda_packages/customer_notifier.zip"

  source {
    content  = file("${path.module}/lambda_functions/customer_notifier.py")
    filename = "lambda_function.py"
  }
}

# CloudWatch Log Group for Customer Notifier
resource "aws_cloudwatch_log_group" "lambda_customer_notifier" {
  name              = "/aws/lambda/${var.environment}-${var.project_name}-customer-notifier"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.enable_log_encryption ? aws_kms_key.s3_data_lake.arn : null

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-customer-notifier-logs"
    Component  = "Logging"
    Purpose    = "Lambda Function Logs"
    CostCenter = var.cost_center
  })
}

# Dead Letter Queue for Customer Notifier
resource "aws_sqs_queue" "customer_notifier_dlq" {
  name                      = "${var.environment}-${var.project_name}-customer-notifier-dlq"
  message_retention_seconds = 1209600 # 14 days
  kms_master_key_id         = aws_kms_key.s3_data_lake.key_id

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-customer-notifier-dlq"
    Component  = "Messaging"
    Purpose    = "Lambda Error Handling"
    CostCenter = var.cost_center
  })
}

# ============================================================================
# SNS Topic for Customer Alerts
# ============================================================================

# SNS Topic for customer alerts and notifications
resource "aws_sns_topic" "customer_alerts" {
  name              = "${var.environment}-${var.project_name}-customer-alerts"
  kms_master_key_id = aws_kms_key.s3_data_lake.key_id

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-customer-alerts"
    Component  = "Messaging"
    Purpose    = "Customer Alert Distribution"
    CostCenter = var.cost_center
  })
}

# Email subscription for SNS topic (for demo purposes)
resource "aws_sns_topic_subscription" "customer_alerts_email" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.customer_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ============================================================================
# Lambda Security Group
# ============================================================================

# Security Group for Lambda functions
resource "aws_security_group" "lambda_functions" {
  name_prefix = "${var.environment}-${var.project_name}-lambda-"
  vpc_id      = var.vpc_id
  description = "Security group for Lambda functions"

  # Allow outbound HTTPS for AWS API calls
  egress {
    description = "HTTPS outbound"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow outbound HTTP for external APIs
  egress {
    description = "HTTP outbound"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow communication with S3 VPC endpoint (if exists)
  egress {
    description = "S3 VPC endpoint"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-lambda-sg"
    Component  = "Security"
    Purpose    = "Lambda Function Network Access"
    CostCenter = var.cost_center
  })

  lifecycle {
    create_before_destroy = true
  }
}

# ============================================================================
# Lambda IAM Roles and Policies
# ============================================================================

# IAM role for Lambda function execution
resource "aws_iam_role" "lambda_execution_role" {
  name_prefix = "${var.environment}-${var.project_name}-lambda-execution-"

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

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-lambda-execution-role"
    Component  = "IAM"
    Purpose    = "Lambda Function Execution"
    CostCenter = var.cost_center
  })
}

# Attach AWS managed policy for VPC Lambda execution
resource "aws_iam_role_policy_attachment" "lambda_execution_policy" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Custom policy for Lambda functions
resource "aws_iam_role_policy" "lambda_custom_policy" {
  name_prefix = "${var.environment}-${var.project_name}-lambda-custom-"
  role        = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # S3 permissions for data lake access
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:GetObjectVersion"
        ]
        Resource = [
          aws_s3_bucket.bronze_layer.arn,
          "${aws_s3_bucket.bronze_layer.arn}/*",
          aws_s3_bucket.silver_layer.arn,
          "${aws_s3_bucket.silver_layer.arn}/*",
          aws_s3_bucket.gold_layer.arn,
          "${aws_s3_bucket.gold_layer.arn}/*"
        ]
      },
      # KMS permissions for encryption/decryption
      {
        Effect = "Allow"
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = aws_kms_key.s3_data_lake.arn
      },
      # SQS permissions for dead letter queues
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = [
          aws_sqs_queue.data_validator_dlq.arn,
          aws_sqs_queue.analytics_trigger_dlq.arn,
          aws_sqs_queue.customer_notifier_dlq.arn
        ]
      },
      # SNS permissions for notifications
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.customer_alerts.arn
      },
      # CloudWatch metrics permissions
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics"
        ]
        Resource = "*"
      }
    ]
  })
}

# ============================================================================
# Lambda Function Files (Placeholder - Will be created separately)
# ============================================================================

# Create directory for Lambda function packages
resource "null_resource" "lambda_packages_dir" {
  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/lambda_packages"
  }
}

# Create directory for Lambda function source code
resource "null_resource" "lambda_functions_dir" {
  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/lambda_functions"
  }
}
