# ============================================================================
# CAP Demo - MSK Kafka Cluster Configuration
# ============================================================================
# Purpose: Enterprise-grade Apache Kafka cluster using AWS MSK
#
# This configuration implements Toyota CAP-style streaming architecture with:
# - Multi-AZ high availability deployment
# - Enterprise security (TLS encryption, VPC isolation)
# - Cost-optimized settings for demo environment
# - Production-ready patterns that scale
#
# MSK Benefits over self-managed Kafka:
# - Automated cluster management and updates
# - Built-in monitoring and logging integration
# - Multi-AZ fault tolerance
# - Automatic scaling capabilities
# - AWS service integrations (IAM, CloudWatch, etc.)
# ============================================================================

# ============================================================================
# Security Group - Network Access Control for MSK Cluster
# ============================================================================

# Security group controls network access to MSK brokers
# Implements least-privilege access principle with specific port requirements
resource "aws_security_group" "msk_cluster" {
  name_prefix = "${local.name_prefix}-msk-" # Unique naming with prefix
  vpc_id      = aws_vpc.cap_demo.id         # Attach to our VPC
  description = "Security group for MSK Kafka cluster - controls broker access"

  # Kafka broker communication ports
  # Port 9092: Plaintext communication (for demo simplicity)
  # Port 9094: TLS encrypted communication (production recommended)
  # Both ports enabled to support different client configurations
  ingress {
    from_port   = 9092
    to_port     = 9094
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks # Only VPC traffic allowed (10.0.0.0/16)
    description = "Kafka broker access - plaintext (9092) and TLS (9094)"
  }

  # Zookeeper communication port
  # Port 2181: Zookeeper client connections for cluster coordination
  # Required for Kafka metadata management and leader election
  ingress {
    from_port   = 2181
    to_port     = 2181
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "Zookeeper access for cluster coordination"
  }

  # JMX monitoring ports for operational visibility
  # Ports 11001-11002: Java Management Extensions for metrics collection
  # Essential for production monitoring and troubleshooting
  ingress {
    from_port   = 11001
    to_port     = 11002
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "JMX monitoring ports for metrics collection"
  }

  # Outbound traffic - allow all for AWS service communication
  # MSK brokers need outbound access for:
  # - AWS API calls (CloudWatch, IAM, etc.)
  # - Software updates and patches
  # - Cross-AZ cluster communication
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"          # All protocols
    cidr_blocks = ["0.0.0.0/0"] # All destinations
    description = "All outbound traffic for AWS services and updates"
  }
  # Tags for resource identification and management
  # Common tags applied for consistent resource tracking
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-msk-sg" # cap-demo-dev-msk-sg
    Type = "Security"
  })

  # Ensure new security group is created before old one is destroyed
  # Prevents temporary access issues during updates
  lifecycle {
    create_before_destroy = true
  }
}

# ============================================================================
# CloudWatch Log Group - Centralized Logging
# ============================================================================

# CloudWatch log group for MSK broker logs
# Provides centralized logging for troubleshooting and monitoring
resource "aws_cloudwatch_log_group" "msk_logs" {
  count = var.enable_logging ? 1 : 0 # Conditional creation based on variable

  name              = "/aws/msk/${local.name_prefix}-cluster" # Standard MSK log path
  retention_in_days = 7                                       # Short retention for demo cost control (production: 30+ days)

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-msk-logs"
    Type = "Logging"
  }) # Ensure consistent tagging across resources
}

# ============================================================================
# MSK Configuration - Custom Kafka Settings
# ============================================================================

# Custom MSK configuration optimizes Kafka settings for our use case
# Overrides default MSK settings for better performance and demo requirements
resource "aws_msk_configuration" "cap_demo" {
  kafka_versions = [var.kafka_version] # Version compatibility
  name           = "${local.name_prefix}-config"
  description    = "MSK configuration optimized for CAP demo environment"

  # Kafka server properties - tuned for t3.small instances and demo workloads
  # These settings balance performance, reliability, and resource usage
  server_properties = <<-EOT
    # Topic Management Settings
    auto.create.topics.enable=true
    default.replication.factor=2
    min.insync.replicas=1
    num.partitions=3

    # Data Retention Settings - optimized for demo environment
    log.retention.hours=24
    log.retention.bytes=1073741824
    log.segment.bytes=104857600

    # Performance Settings - tuned for t3.small instances (2 vCPU, 2GB RAM)
    num.network.threads=3
    num.io.threads=8
    socket.send.buffer.bytes=102400
    socket.receive.buffer.bytes=102400
    socket.request.max.bytes=104857600

    # Producer/Consumer Optimization
    replica.fetch.max.bytes=1048576
    message.max.bytes=1000000

    # Monitoring configuration removed - using CloudWatch instead
  EOT
}

# ============================================================================
# MSK Cluster - Main Kafka Infrastructure
# ============================================================================

# MSK cluster - the core Kafka infrastructure for the CAP demo
# Implements enterprise-grade streaming with AWS-managed operations
resource "aws_msk_cluster" "cap_demo" {
  cluster_name           = "${local.name_prefix}-cluster"            # cap-demo-dev-cluster
  kafka_version          = var.kafka_version                         # 2.8.1 for stability
  number_of_broker_nodes = var.kafka_num_brokers * length(local.azs) # 3 brokers total (1 per AZ)

  # Apply our custom configuration for optimal performance
  configuration_info {
    arn      = aws_msk_configuration.cap_demo.arn
    revision = aws_msk_configuration.cap_demo.latest_revision
  }

  # Broker node configuration - defines compute and storage resources
  broker_node_group_info {
    instance_type   = var.kafka_instance_type             # kafka.t3.small for cost optimization
    client_subnets  = aws_subnet.private[*].id            # Deploy in private subnets for security
    security_groups = [aws_security_group.msk_cluster.id] # Apply security group rules

    # EBS storage configuration for broker data persistence
    storage_info {
      ebs_storage_info {
        volume_size = var.kafka_ebs_volume_size # 100GB per broker for demo
      }
    }
  }

  # Client authentication configuration
  # Supports unauthenticated access for demo simplicity and reliability
  client_authentication {
    unauthenticated = true # Allow unauthenticated access for demo ease
  }

  # Encryption configuration for data security
  # Implements defense-in-depth with multiple encryption layers
  encryption_info {
    encryption_in_transit {
      client_broker = "TLS_PLAINTEXT" # Support both TLS and plaintext for demo flexibility
      in_cluster    = true            # Encrypt inter-broker communication
    }
    # Note: At-rest encryption uses service-managed keys for demo simplicity
    # Production would typically use customer-managed KMS keys
  }

  # Enhanced monitoring configuration
  # Disabled for cost control but easily enabled for production
  enhanced_monitoring = var.enable_monitoring ? "PER_TOPIC_PER_BROKER" : "DEFAULT"

  # CloudWatch logging configuration
  # Conditional logging based on variable for cost control
  dynamic "logging_info" {
    for_each = var.enable_logging ? [1] : []
    content {
      broker_logs {
        cloudwatch_logs {
          enabled   = true
          log_group = aws_cloudwatch_log_group.msk_logs[0].name
        }
        firehose {
          enabled = false # Firehose disabled for demo cost control
        }
        s3 {
          enabled = false # S3 logging disabled for demo cost control
        }
      }
    }
  }

  # Prometheus monitoring configuration
  # Optional advanced monitoring for production environments
  dynamic "open_monitoring" {
    for_each = var.enable_prometheus ? [1] : []
    content {
      prometheus {
        jmx_exporter {
          enabled_in_broker = true # Enable JMX metrics export
        }
        node_exporter {
          enabled_in_broker = true # Enable OS-level metrics export
        }
      }
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-msk-cluster"
    Type = "Kafka"
  })

  # Ensure network infrastructure is fully operational before cluster creation
  # Critical for proper cluster initialization and networking
  depends_on = [
    aws_internet_gateway.cap_demo,
    aws_route_table_association.private
  ]
}

# ============================================================================
# KMS Key - Encryption Key Management
# ============================================================================

# KMS key for additional encryption capabilities
# Provides customer-managed encryption for enhanced security control
resource "aws_kms_key" "msk" {
  description             = "KMS key for MSK cluster encryption and security"
  deletion_window_in_days = 7 # Short deletion window for demo (production: 30 days)

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-msk-key"
    Type = "Security"
  })
}

# KMS key alias for easier identification and management
# Provides human-readable name for the encryption key
resource "aws_kms_alias" "msk" {
  name          = "alias/${local.name_prefix}-msk" # alias/cap-demo-dev-msk
  target_key_id = aws_kms_key.msk.key_id
}
