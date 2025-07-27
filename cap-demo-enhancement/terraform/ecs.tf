# ============================================================================
# CAP Demo Project - Phase 2: ECS Data Processing Infrastructure
# ============================================================================
# Purpose: Deploy ECS Fargate cluster with data processing services
#
# This file creates the container orchestration layer that processes data
# from the MSK Kafka cluster (Phase 1) and writes to S3 data lake.
#
# Key Components:
# - ECS Fargate Cluster for serverless container execution
# - Application Load Balancer for health checks and service discovery
# - Auto Scaling policies based on Kafka consumer lag and CPU usage
# - Service definitions for security, metrics, and workflow processors
# - Task definitions with optimized resource allocation
# - CloudWatch integration for monitoring and alerting
#
# Integration Points:
# - Uses VPC and subnets from Phase 1 (network.tf)
# - Connects to MSK cluster for data consumption
# - Writes processed data to S3 buckets (s3.tf)
# - Integrates with Lambda functions for event-driven processing
#
# Cost Optimization:
# - Fargate Spot pricing where applicable
# - Resource-optimized task definitions
# - Scheduled scaling for predictable workloads
# - Efficient container image sizes
# ============================================================================

# ECS Cluster for data processing services
# Uses Fargate for serverless container execution - no EC2 management required
# Enables Container Insights for advanced monitoring and troubleshooting
resource "aws_ecs_cluster" "main" {
  name = "${var.environment}-${var.project_name}-cluster"

  # Enable CloudWatch Container Insights for advanced monitoring
  # Provides CPU, memory, network, and storage metrics per container
  setting {
    name  = "containerInsights"
    value = var.enable_container_insights ? "enabled" : "disabled"
  }

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-ecs-cluster"
    Component  = "Container Orchestration"
    Purpose    = "Data Processing Services"
    CostCenter = var.cost_center
  })
}

# Application Load Balancer for ECS services
# Provides health checks, service discovery, and traffic distribution
# Internal-facing since services communicate within VPC
resource "aws_lb" "ecs_alb" {
  name               = "${var.environment}-${var.project_name}-ecs-alb"
  internal           = true # Internal ALB for service-to-service communication
  load_balancer_type = "application"
  security_groups    = [aws_security_group.ecs_alb.id]
  subnets            = aws_subnet.private[*].id # Deploy in private subnets

  # Enable deletion protection in production environments
  enable_deletion_protection = var.environment == "prod" ? true : false

  # Enable access logs for debugging and compliance
  # Logs are stored in S3 for analysis and audit trail
  access_logs {
    bucket  = aws_s3_bucket.ecs_logs.bucket
    prefix  = "alb-access-logs"
    enabled = var.enable_access_logs
  }

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-ecs-alb"
    Component  = "Load Balancing"
    Purpose    = "ECS Service Health Checks"
    CostCenter = var.cost_center
  })
}

# S3 bucket for ALB access logs
# Required for compliance and troubleshooting ECS service health
resource "aws_s3_bucket" "ecs_logs" {
  bucket = "${var.environment}-${var.project_name}-ecs-logs-${random_string.bucket_suffix.result}"

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-ecs-logs"
    Component  = "Logging"
    Purpose    = "ALB Access Logs"
    CostCenter = var.cost_center
  })
}

# Random string defined in main.tf

# S3 bucket versioning for log retention and compliance
resource "aws_s3_bucket_versioning" "ecs_logs" {
  bucket = aws_s3_bucket.ecs_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket lifecycle policy for cost optimization
# Automatically transitions logs to cheaper storage classes
resource "aws_s3_bucket_lifecycle_configuration" "ecs_logs" {
  bucket = aws_s3_bucket.ecs_logs.id

  rule {
    id     = "log_lifecycle"
    status = "Enabled"

    filter {
      prefix = ""
    }

    # Move to Infrequent Access after 30 days
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    # Move to Glacier after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # Delete after 1 year (adjust based on compliance requirements)
    expiration {
      days = 365
    }
  }
}

# Security Group for ALB
# Controls inbound traffic to the load balancer
resource "aws_security_group" "ecs_alb" {
  name_prefix = "${var.environment}-${var.project_name}-ecs-alb-"
  vpc_id      = aws_vpc.cap_demo.id
  description = "Security group for ECS Application Load Balancer"

  # Allow HTTP traffic from within VPC
  # Used for health checks and internal service communication
  ingress {
    description = "HTTP from VPC"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.cap_demo.cidr_block]
  }

  # Allow HTTPS traffic from within VPC
  # Encrypted communication between services
  ingress {
    description = "HTTPS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.cap_demo.cidr_block]
  }

  # Allow all outbound traffic for service communication
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-ecs-alb-sg"
    Component  = "Security"
    Purpose    = "ALB Traffic Control"
    CostCenter = var.cost_center
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Security Group for ECS Tasks
# Controls traffic to and from container tasks
resource "aws_security_group" "ecs_tasks" {
  name_prefix = "${var.environment}-${var.project_name}-ecs-tasks-"
  vpc_id      = aws_vpc.cap_demo.id
  description = "Security group for ECS tasks"

  # Allow traffic from ALB on container ports
  ingress {
    description     = "Traffic from ALB"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_alb.id]
  }

  # Allow Kafka client connections to MSK cluster
  # Required for consuming data from Kafka topics
  ingress {
    description = "Kafka client connections"
    from_port   = 9092
    to_port     = 9094
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.cap_demo.cidr_block]
  }

  # Allow outbound HTTPS for AWS API calls
  # Required for S3, CloudWatch, and other AWS service interactions
  egress {
    description = "HTTPS outbound"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow outbound HTTP for health checks and external APIs
  egress {
    description = "HTTP outbound"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow Kafka producer/consumer traffic
  egress {
    description = "Kafka traffic"
    from_port   = 9092
    to_port     = 9094
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.cap_demo.cidr_block]
  }

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-ecs-tasks-sg"
    Component  = "Security"
    Purpose    = "ECS Task Traffic Control"
    CostCenter = var.cost_center
  })

  lifecycle {
    create_before_destroy = true
  }
}

# CloudWatch Log Group for ECS task logs
# Centralized logging for all container applications
resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/${var.environment}-${var.project_name}"
  retention_in_days = var.log_retention_days

  # Enable encryption for log data at rest
  kms_key_id = var.enable_log_encryption ? aws_kms_key.logs[0].arn : null

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-ecs-logs"
    Component  = "Logging"
    Purpose    = "ECS Task Logs"
    CostCenter = var.cost_center
  })
}

# KMS key for log encryption (conditional)
# Encrypts CloudWatch logs for enhanced security
resource "aws_kms_key" "logs" {
  count = var.enable_log_encryption ? 1 : 0

  description             = "KMS key for ${var.environment}-${var.project_name} ECS logs encryption"
  deletion_window_in_days = var.kms_deletion_window
  enable_key_rotation     = true

  # Key policy allowing CloudWatch Logs service to use the key
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
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.amazonaws.com"
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
    Name       = "${var.environment}-${var.project_name}-ecs-logs-kms"
    Component  = "Security"
    Purpose    = "ECS Logs Encryption"
    CostCenter = var.cost_center
  })
}

# KMS key alias for easier management
resource "aws_kms_alias" "logs" {
  count = var.enable_log_encryption ? 1 : 0

  name          = "alias/${var.environment}-${var.project_name}-ecs-logs"
  target_key_id = aws_kms_key.logs[0].key_id
}

# Data sources defined in main.tf

# IAM role for ECS task execution
# Allows ECS to pull container images and write logs
resource "aws_iam_role" "ecs_execution_role" {
  name_prefix = "${var.environment}-${var.project_name}-ecs-execution-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-ecs-execution-role"
    Component  = "IAM"
    Purpose    = "ECS Task Execution"
    CostCenter = var.cost_center
  })
}

# Attach AWS managed policy for ECS task execution
resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Custom policy for additional ECS execution permissions
# Includes KMS permissions for log encryption and ECR access
resource "aws_iam_role_policy" "ecs_execution_custom" {
  name_prefix = "${var.environment}-${var.project_name}-ecs-execution-custom-"
  role        = aws_iam_role.ecs_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat([
      # CloudWatch Logs permissions
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "${aws_cloudwatch_log_group.ecs_logs.arn}:*"
      },
      # ECR permissions for container image access
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      }
      ], var.enable_log_encryption ? [
      # KMS permissions for log encryption (conditional)
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = aws_kms_key.logs[0].arn
      }
    ] : [])
  })
}

# IAM role for ECS tasks (application permissions)
# Allows tasks to interact with AWS services (S3, MSK, etc.)
resource "aws_iam_role" "ecs_task_role" {
  name_prefix = "${var.environment}-${var.project_name}-ecs-task-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-ecs-task-role"
    Component  = "IAM"
    Purpose    = "ECS Task Application Permissions"
    CostCenter = var.cost_center
  })
}

# Custom policy for ECS task application permissions
resource "aws_iam_role_policy" "ecs_task_custom" {
  name_prefix = "${var.environment}-${var.project_name}-ecs-task-custom-"
  role        = aws_iam_role.ecs_task_role.id

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
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.environment}-${var.project_name}-data-lake*",
          "arn:aws:s3:::${var.environment}-${var.project_name}-data-lake*/*"
        ]
      },
      # MSK permissions for Kafka access
      {
        Effect = "Allow"
        Action = [
          "kafka:DescribeCluster",
          "kafka:GetBootstrapBrokers",
          "kafka:ListClusters"
        ]
        Resource = "*"
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
      },
      # SSM Parameter Store for configuration
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/${var.environment}/${var.project_name}/*"
      }
    ]
  })
}

# Data source for current AWS region
data "aws_region" "current" {}

# ============================================================================
# ECS Service Definitions
# ============================================================================

# Security Event Processor Service
# Processes security logs and audit trails from Kafka
module "security_processor_service" {
  source = "./modules/ecs_service"

  # Service configuration
  service_name = "security-processor"
  cluster_id   = aws_ecs_cluster.main.id

  # Task definition
  container_image = var.security_processor_image
  container_port  = 8080
  cpu             = var.security_processor_cpu
  memory          = var.security_processor_memory

  # Networking
  vpc_id           = aws_vpc.cap_demo.id
  private_subnets  = aws_subnet.private[*].id
  security_groups  = [aws_security_group.ecs_tasks.id]
  target_group_arn = aws_lb_target_group.security_processor.arn

  # Scaling
  desired_count = var.security_processor_desired_count
  min_capacity  = var.security_processor_min_capacity
  max_capacity  = var.security_processor_max_capacity

  # IAM roles
  execution_role_arn = aws_iam_role.ecs_execution_role.arn
  task_role_arn      = aws_iam_role.ecs_task_role.arn

  # Logging
  log_group_name = aws_cloudwatch_log_group.ecs_logs.name

  # Environment variables
  environment_variables = {
    KAFKA_BOOTSTRAP_SERVERS = var.kafka_bootstrap_servers
    S3_DATA_BUCKET          = var.s3_data_bucket
    ENVIRONMENT             = var.environment
    SERVICE_NAME            = "security-processor"
  }

  # Common tags
  common_tags = var.common_tags
}

# ALB Target Group for Security Processor
resource "aws_lb_target_group" "security_processor" {
  name        = "${var.environment}-${var.project_name}-security-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = aws_vpc.cap_demo.id
  target_type = "ip"

  # Health check configuration
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 10
    interval            = 30
    path                = "/health"
    matcher             = "200"
    protocol            = "HTTP"
    port                = "traffic-port"
  }

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-security-tg"
    Component  = "Load Balancing"
    Purpose    = "Security Processor Health Checks"
    CostCenter = var.cost_center
  })
}

# ALB Listener for Security Processor
resource "aws_lb_listener" "security_processor" {
  load_balancer_arn = aws_lb.ecs_alb.arn
  port              = "8080"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.security_processor.arn
  }

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-security-listener"
    Component  = "Load Balancing"
    Purpose    = "Security Processor Routing"
    CostCenter = var.cost_center
  })
}

# Application Metrics Processor Service
# Processes performance metrics and database logs
module "metrics_processor_service" {
  source = "./modules/ecs_service"

  # Service configuration
  service_name = "metrics-processor"
  cluster_id   = aws_ecs_cluster.main.id

  # Task definition
  container_image = var.metrics_processor_image
  container_port  = 8080
  cpu             = var.metrics_processor_cpu
  memory          = var.metrics_processor_memory

  # Networking
  vpc_id           = aws_vpc.cap_demo.id
  private_subnets  = aws_subnet.private[*].id
  security_groups  = [aws_security_group.ecs_tasks.id]
  target_group_arn = aws_lb_target_group.metrics_processor.arn

  # Scaling
  desired_count = var.metrics_processor_desired_count
  min_capacity  = var.metrics_processor_min_capacity
  max_capacity  = var.metrics_processor_max_capacity

  # IAM roles
  execution_role_arn = aws_iam_role.ecs_execution_role.arn
  task_role_arn      = aws_iam_role.ecs_task_role.arn

  # Logging
  log_group_name = aws_cloudwatch_log_group.ecs_logs.name

  # Environment variables
  environment_variables = {
    KAFKA_BOOTSTRAP_SERVERS = var.kafka_bootstrap_servers
    S3_DATA_BUCKET          = var.s3_data_bucket
    ENVIRONMENT             = var.environment
    SERVICE_NAME            = "metrics-processor"
  }

  # Common tags
  common_tags = var.common_tags
}

# ALB Target Group for Metrics Processor
resource "aws_lb_target_group" "metrics_processor" {
  name        = "${var.environment}-${var.project_name}-metrics-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = aws_vpc.cap_demo.id
  target_type = "ip"

  # Health check configuration
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 10
    interval            = 30
    path                = "/health"
    matcher             = "200"
    protocol            = "HTTP"
    port                = "traffic-port"
  }

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-metrics-tg"
    Component  = "Load Balancing"
    Purpose    = "Metrics Processor Health Checks"
    CostCenter = var.cost_center
  })
}

# ALB Listener for Metrics Processor
resource "aws_lb_listener" "metrics_processor" {
  load_balancer_arn = aws_lb.ecs_alb.arn
  port              = "8081"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.metrics_processor.arn
  }

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-metrics-listener"
    Component  = "Load Balancing"
    Purpose    = "Metrics Processor Routing"
    CostCenter = var.cost_center
  })
}

# Customer Workflow Processor Service
# Handles customer events and workflow automation
module "workflow_processor_service" {
  source = "./modules/ecs_service"

  # Service configuration
  service_name = "workflow-processor"
  cluster_id   = aws_ecs_cluster.main.id

  # Task definition
  container_image = var.workflow_processor_image
  container_port  = 8080
  cpu             = var.workflow_processor_cpu
  memory          = var.workflow_processor_memory

  # Networking
  vpc_id           = aws_vpc.cap_demo.id
  private_subnets  = aws_subnet.private[*].id
  security_groups  = [aws_security_group.ecs_tasks.id]
  target_group_arn = aws_lb_target_group.workflow_processor.arn

  # Scaling
  desired_count = var.workflow_processor_desired_count
  min_capacity  = var.workflow_processor_min_capacity
  max_capacity  = var.workflow_processor_max_capacity

  # IAM roles
  execution_role_arn = aws_iam_role.ecs_execution_role.arn
  task_role_arn      = aws_iam_role.ecs_task_role.arn

  # Logging
  log_group_name = aws_cloudwatch_log_group.ecs_logs.name

  # Environment variables
  environment_variables = {
    KAFKA_BOOTSTRAP_SERVERS = var.kafka_bootstrap_servers
    S3_DATA_BUCKET          = var.s3_data_bucket
    ENVIRONMENT             = var.environment
    SERVICE_NAME            = "workflow-processor"
  }

  # Common tags
  common_tags = var.common_tags
}

# ALB Target Group for Workflow Processor
resource "aws_lb_target_group" "workflow_processor" {
  name        = "${var.environment}-${var.project_name}-workflow-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = aws_vpc.cap_demo.id
  target_type = "ip"

  # Health check configuration
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 10
    interval            = 30
    path                = "/health"
    matcher             = "200"
    protocol            = "HTTP"
    port                = "traffic-port"
  }

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-workflow-tg"
    Component  = "Load Balancing"
    Purpose    = "Workflow Processor Health Checks"
    CostCenter = var.cost_center
  })
}

# ALB Listener for Workflow Processor
resource "aws_lb_listener" "workflow_processor" {
  load_balancer_arn = aws_lb.ecs_alb.arn
  port              = "8082"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.workflow_processor.arn
  }

  tags = merge(var.common_tags, {
    Name       = "${var.environment}-${var.project_name}-workflow-listener"
    Component  = "Load Balancing"
    Purpose    = "Workflow Processor Routing"
    CostCenter = var.cost_center
  })
}
