# CAP Demo - Data Processors

This directory contains the containerized data processing applications that run on ECS Fargate.

## Applications

1. **Security Event Processor** (`security_processor/`)
   - Processes security logs and alerts from Kafka
   - Implements threat detection and classification
   - Outputs to S3 and alerts Lambda functions

2. **Application Metrics Processor** (`metrics_processor/`)
   - Processes application performance metrics
   - Calculates aggregations and trends
   - Stores processed data in S3 data lake

3. **Customer Onboarding Processor** (`onboarding_processor/`)
   - Handles new customer workflow automation
   - Processes JIRA integration events
   - Manages customer topic provisioning

## Container Architecture

Each processor is a Python application that:
- Connects to MSK Kafka as a consumer
- Processes streaming data in real-time
- Stores results in S3 Bronze/Silver/Gold layers
- Publishes alerts and notifications
- Provides health checks and metrics

## Deployment

Containers are deployed via ECS Fargate using Terraform configuration in `terraform/ecs.tf`.
