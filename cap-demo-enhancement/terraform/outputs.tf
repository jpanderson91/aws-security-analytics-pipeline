# CAP Demo - Infrastructure Outputs
# Important information for connecting to MSK cluster

# VPC Information
output "vpc_id" {
  description = "ID of the VPC created for CAP demo"
  value       = aws_vpc.cap_demo.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.cap_demo.cidr_block
}

output "private_subnet_ids" {
  description = "IDs of private subnets where MSK cluster is deployed"
  value       = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  description = "IDs of public subnets for NAT gateways and bastion hosts"
  value       = aws_subnet.public[*].id
}

# MSK Cluster Information
output "msk_cluster_arn" {
  description = "ARN of the MSK cluster"
  value       = aws_msk_cluster.cap_demo.arn
}

output "msk_cluster_name" {
  description = "Name of the MSK cluster"
  value       = aws_msk_cluster.cap_demo.cluster_name
}

output "msk_kafka_version" {
  description = "Kafka version of the MSK cluster"
  value       = aws_msk_cluster.cap_demo.kafka_version
}

output "msk_bootstrap_brokers" {
  description = "Bootstrap brokers for connecting to MSK cluster (plaintext)"
  value       = aws_msk_cluster.cap_demo.bootstrap_brokers
}

output "msk_bootstrap_brokers_tls" {
  description = "Bootstrap brokers for connecting to MSK cluster (TLS)"
  value       = aws_msk_cluster.cap_demo.bootstrap_brokers_tls
}

# ECS Cluster Information (Phase 2)
output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

# ECS Service Information
output "ecs_security_processor_service_name" {
  description = "Name of the security processor ECS service"
  value       = module.security_processor_service.service_name
}

output "ecs_metrics_processor_service_name" {
  description = "Name of the metrics processor ECS service"
  value       = module.metrics_processor_service.service_name
}

# S3 Data Lake Information (Phase 2)
output "s3_bronze_bucket_name" {
  description = "Name of the S3 Bronze data lake bucket"
  value       = aws_s3_bucket.bronze_layer.bucket
}

output "s3_bronze_bucket_arn" {
  description = "ARN of the S3 Bronze data lake bucket"
  value       = aws_s3_bucket.bronze_layer.arn
}

output "s3_silver_bucket_name" {
  description = "Name of the S3 Silver data lake bucket"
  value       = aws_s3_bucket.silver_layer.bucket
}

output "s3_silver_bucket_arn" {
  description = "ARN of the S3 Silver data lake bucket"
  value       = aws_s3_bucket.silver_layer.arn
}

output "s3_gold_bucket_name" {
  description = "Name of the S3 Gold data lake bucket"
  value       = aws_s3_bucket.gold_layer.bucket
}

output "s3_gold_bucket_arn" {
  description = "ARN of the S3 Gold data lake bucket"
  value       = aws_s3_bucket.gold_layer.arn
}

# Lambda Function Information (Phase 2)
output "lambda_data_validator_arn" {
  description = "ARN of the data validator Lambda function"
  value       = aws_lambda_function.data_validator.arn
}

output "lambda_analytics_trigger_arn" {
  description = "ARN of the analytics trigger Lambda function"
  value       = aws_lambda_function.analytics_trigger.arn
}

output "lambda_customer_notifier_arn" {
  description = "ARN of the customer notifier Lambda function"
  value       = aws_lambda_function.customer_notifier.arn
}

output "msk_zookeeper_connect_string" {
  description = "Zookeeper connection string for the MSK cluster"
  value       = aws_msk_cluster.cap_demo.zookeeper_connect_string
}

# Security Information
output "msk_security_group_id" {
  description = "Security group ID for MSK cluster"
  value       = aws_security_group.msk_cluster.id
}

output "kms_key_id" {
  description = "KMS key ID for MSK encryption"
  value       = aws_kms_key.msk.key_id
}

output "kms_key_arn" {
  description = "KMS key ARN for MSK encryption"
  value       = aws_kms_key.msk.arn
}

# Connection Information for Demo
output "demo_connection_info" {
  description = "Connection information for CAP demo scenarios"
  value = {
    cluster_name      = aws_msk_cluster.cap_demo.cluster_name
    bootstrap_servers = aws_msk_cluster.cap_demo.bootstrap_brokers
    security_group    = aws_security_group.msk_cluster.id
    vpc_id            = aws_vpc.cap_demo.id
    private_subnets   = aws_subnet.private[*].id
    demo_topics       = var.demo_topics
  }
}

# Cost Information
output "estimated_monthly_cost" {
  description = "Estimated monthly cost for MSK infrastructure"
  value = {
    msk_brokers    = "~$45-60/month (${var.kafka_num_brokers * length(local.azs)} x ${var.kafka_instance_type})"
    ebs_storage    = "~$10-15/month (${var.kafka_ebs_volume_size * var.kafka_num_brokers * length(local.azs)}GB)"
    nat_gateways   = "~$45/month (${length(local.azs)} NAT gateways)"
    total_estimate = "~$100-120/month"
    demo_duration  = "Expected demo duration: 2-3 days (~$10-15 total)"
  }
}

# Environment Information
output "environment_info" {
  description = "Environment configuration details"
  value = {
    environment = var.environment
    region      = var.aws_region
    azs         = local.azs
    name_prefix = local.name_prefix
  }
}
