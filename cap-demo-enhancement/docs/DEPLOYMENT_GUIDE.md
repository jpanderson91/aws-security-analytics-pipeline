# CAP Deployment Guide

## 🎯 Prerequisites

### Required Software
- **AWS CLI** v2.0+ configured with appropriate credentials
- **Terraform** v1.0+ for infrastructure provisioning
- **Python** 3.9+ with pip package manager
- **Docker** (optional, for local development)

### AWS Account Setup
- AWS account with administrative privileges
- AWS SSO configured (recommended) or access keys
- Sufficient service quotas for MSK, ECS, Lambda
- Billing alerts configured for cost monitoring

### Permissions Required
- EC2 full access (for MSK networking)
- MSK full access
- ECS full access
- Lambda full access
- S3 full access
- IAM role creation and management
- VPC and networking permissions

## 🚀 Quick Start Deployment

### 1. Environment Setup

```bash
# Clone repository (if not already done)
git clone <repository-url>
cd cap-security-analytics-pipeline

# Create and activate virtual environment
python -m venv cap-env
source cap-env/bin/activate  # Linux/Mac
# or
cap-env\Scripts\activate     # Windows

# Install Python dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure sso  # Recommended
# or
aws configure      # Traditional access keys
```

### 2. Phase 1: Data Ingestion Infrastructure

```bash
# Deploy MSK cluster and networking
python scripts/setup_phase1_kafka.py

# Verify deployment
python scripts/verify_phase1.py
```

**Expected Deployment Time**: 15-20 minutes

**What Gets Created**:
- VPC with public/private subnets
- MSK cluster with 3 brokers
- Security groups for network access
- Kafka topics for security events
- IAM roles and policies

### 3. Phase 2: Data Processing Pipeline

```bash
# Deploy ECS cluster and Lambda functions
python scripts/setup_phase2_processing.py

# Verify deployment
python scripts/verify_phase2.py
```

**Expected Deployment Time**: 10-15 minutes

**What Gets Created**:
- ECS Fargate cluster
- Lambda functions for event processing
- S3 buckets (Bronze/Silver/Gold)
- Glue catalog and tables
- SQS queues for message handling

### 4. Phase 3: Analytics and APIs

```bash
# Deploy QuickSight and API Gateway
python scripts/setup_phase3_analytics.py

# Verify deployment
python scripts/verify_phase3.py
```

**Expected Deployment Time**: 8-12 minutes

**What Gets Created**:
- API Gateway with Lambda integration
- DynamoDB tables for metadata
- Athena workgroup for analytics
- QuickSight setup (if user configured)
- CloudWatch dashboards

## 🔧 Detailed Configuration

### Environment Variables

Create a `.env` file with your specific configuration:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=cap-demo

# Project Configuration
PROJECT_NAME=cap-security-analytics
ENVIRONMENT=dev  # dev, staging, prod

# Network Configuration
VPC_CIDR=10.0.0.0/16
ENABLE_NAT_GATEWAY=true

# MSK Configuration
MSK_INSTANCE_TYPE=kafka.t3.small
MSK_EBS_VOLUME_SIZE=100

# ECS Configuration
ECS_CPU=256
ECS_MEMORY=512
ECS_DESIRED_COUNT=2

# Data Configuration
DATA_RETENTION_DAYS=30
ENABLE_S3_VERSIONING=true
```

### Terraform Variables

Customize deployment by modifying `terraform/terraform.tfvars`:

```hcl
# Project Settings
project_name = "cap-security-analytics"
environment  = "dev"
region      = "us-east-1"

# Network Settings
vpc_cidr = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

# MSK Settings
msk_instance_type = "kafka.t3.small"
msk_kafka_version = "2.8.1"
msk_number_of_broker_nodes = 3

# ECS Settings
ecs_task_cpu    = 256
ecs_task_memory = 512
ecs_desired_count = 2

# Data Settings
s3_lifecycle_transition_days = 30
enable_s3_versioning = true
```

## 🎯 Phase-by-Phase Deployment Details

### Phase 1: MSK and Networking

**Components Deployed**:
1. **VPC Infrastructure**
   - VPC with DNS resolution enabled
   - Public subnets for NAT gateways
   - Private subnets for MSK brokers
   - Internet and NAT gateways
   - Route tables and associations

2. **MSK Cluster**
   - Multi-AZ Kafka cluster
   - Encryption in transit and at rest
   - Client authentication (IAM)
   - Monitoring and logging enabled

3. **Security Configuration**
   - Security groups with minimal access
   - IAM roles for MSK access
   - VPC endpoints for AWS services

**Validation Steps**:
```bash
# Check VPC creation
aws ec2 describe-vpcs --filters "Name=tag:Project,Values=cap-security-analytics"

# Check MSK cluster status
aws kafka describe-cluster --cluster-arn <cluster-arn>

# Test Kafka connectivity
python scripts/test_kafka_connection.py
```

### Phase 2: Processing Infrastructure

**Components Deployed**:
1. **ECS Fargate Cluster**
   - Auto-scaling task definitions
   - Service discovery configuration
   - CloudWatch log groups
   - Task roles and execution roles

2. **Lambda Functions**
   - Event processing functions
   - Dead letter queue configuration
   - Environment variables
   - VPC configuration for database access

3. **Data Storage**
   - S3 buckets with proper organization
   - Lifecycle policies for cost optimization
   - Glue catalog for schema management
   - Athena workgroup for analytics

**Validation Steps**:
```bash
# Check ECS cluster
aws ecs describe-clusters --clusters cap-security-analytics

# Check Lambda functions
aws lambda list-functions --function-version ALL

# Test data processing
python scripts/test_data_processing.py
```

### Phase 3: Analytics and APIs

**Components Deployed**:
1. **API Gateway**
   - REST API with multiple endpoints
   - Lambda proxy integration
   - API key authentication
   - Usage plans and throttling

2. **Analytics Infrastructure**
   - Athena workgroup for queries
   - QuickSight data sources (optional)
   - CloudWatch dashboards
   - Custom metrics and alarms

3. **Customer Data Management**
   - DynamoDB tables for metadata
   - Global secondary indexes
   - Auto-scaling configuration
   - Backup and recovery setup

**Validation Steps**:
```bash
# Check API Gateway
aws apigateway get-rest-apis

# Test API endpoints
curl -X GET <api-endpoint>/health

# Check DynamoDB tables
aws dynamodb list-tables
```

## 🔍 Monitoring and Validation

### Complete System Validation

```bash
# Run comprehensive validation
python scripts/run_complete_validation.py

# Test end-to-end data flow
python scripts/run_full_demo.py --scenario all
```

### Health Checks

```bash
# Check all services
python scripts/health_check.py

# Monitor costs
python scripts/cost_monitor.py

# View metrics
python scripts/view_metrics.py
```

## 🚨 Troubleshooting

### Common Issues

1. **MSK Deployment Timeout**
   ```bash
   # Check VPC configuration
   aws ec2 describe-subnets --filters "Name=vpc-id,Values=<vpc-id>"
   
   # Verify MSK cluster logs
   aws logs describe-log-groups --log-group-name-prefix "/aws/msk"
   ```

2. **ECS Tasks Not Starting**
   ```bash
   # Check task definition
   aws ecs describe-task-definition --task-definition cap-event-processor
   
   # View task logs
   aws logs get-log-events --log-group-name /ecs/cap-event-processor
   ```

3. **Lambda Function Errors**
   ```bash
   # Check function configuration
   aws lambda get-function --function-name cap-event-processor
   
   # View function logs
   aws logs get-log-events --log-group-name /aws/lambda/cap-event-processor
   ```

4. **API Gateway 500 Errors**
   ```bash
   # Check API Gateway logs
   aws logs get-log-events --log-group-name API-Gateway-Execution-Logs
   
   # Test Lambda integration
   aws lambda invoke --function-name cap-api-handler response.json
   ```

### Debug Commands

```bash
# Enable Terraform debug logging
export TF_LOG=DEBUG

# Enable AWS CLI debug
aws configure set cli_follow_redirects false
aws configure set cli_timestamp_format iso8601

# Check resource dependencies
python scripts/check_dependencies.py

# Validate Terraform configuration
terraform validate
terraform plan
```

### Recovery Procedures

```bash
# Partial failure recovery
python scripts/recover_deployment.py --phase <phase-number>

# Complete environment cleanup
python scripts/cleanup_environment.py --confirm

# Redeploy specific components
python scripts/redeploy_component.py --component <component-name>
```

## 💰 Cost Management

### Cost Monitoring

```bash
# Check current costs
python scripts/get_current_costs.py

# Set up billing alerts
python scripts/setup_billing_alerts.py --threshold 100
```

### Cost Optimization

1. **Right-sizing Resources**
   - Monitor CloudWatch metrics
   - Adjust ECS task definitions
   - Optimize Lambda memory allocation

2. **Data Lifecycle Management**
   - Configure S3 lifecycle policies
   - Archive old data to Glacier
   - Clean up test data regularly

3. **Reserved Capacity**
   - Consider reserved instances for predictable workloads
   - Use Savings Plans for flexible compute usage

## 🔄 Updates and Maintenance

### Regular Maintenance Tasks

```bash
# Update Terraform modules
terraform get -update

# Update Lambda function code
python scripts/update_lambda_functions.py

# Rotate secrets and keys
python scripts/rotate_secrets.py

# Clean up old resources
python scripts/cleanup_old_resources.py
```

### Version Updates

```bash
# Update to new version
git pull origin main
python scripts/update_deployment.py --version <new-version>

# Rollback if needed
python scripts/rollback_deployment.py --version <previous-version>
```

This deployment guide provides comprehensive instructions for setting up and maintaining the CAP security analytics pipeline in your AWS environment.
