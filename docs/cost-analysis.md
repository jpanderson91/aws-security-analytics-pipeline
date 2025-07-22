# AWS Security Analytics Pipeline - Cost Analysis

## Cost Optimization Summary

This document provides a detailed cost analysis for the AWS Security Analytics Pipeline and recommendations for cost optimization in a development/portfolio environment.

## Current Configuration Cost Estimates

### Standard Configuration (terraform.tfvars)
- **Monthly Cost: ~$50-150**
- **Most Expensive Component: GuardDuty (~$30-100/month)**

### Cost-Optimized Configuration (terraform-cost-optimized.tfvars)
- **Monthly Cost: ~$15-25**
- **Primary Savings: GuardDuty disabled (-$30-100/month)**

## Detailed Cost Breakdown

### 1. Kinesis Data Stream
- **Cost**: $10.80/month (1 shard)
- **Optimization**: Already minimal (1 shard)
- **Required**: Yes (core functionality)

### 2. Lambda Function
- **Standard**: 512MB memory
- **Optimized**: 256MB memory (50% cost reduction on execution)
- **Monthly Cost**: $0.50-5 (mostly covered by free tier)

### 3. S3 Storage
- **Lifecycle Rules**: Automatic tiering (Standard → IA → Glacier)
- **Retention**: Reduced from 90 to 30 days
- **Monthly Cost**: $2-10 (depends on data volume)

### 4. GuardDuty (Optional)
- **Standard**: Enabled ($30-100/month)
- **Optimized**: Disabled (can enable manually for testing)
- **Savings**: $30-100/month

### 5. CloudTrail
- **Cost**: $2-5/month
- **Note**: Management events are free; data events cost extra
- **Required**: Yes (provides security events)

### 6. CloudWatch Logs
- **Standard**: 14-day retention
- **Optimized**: 7-day retention
- **Monthly Cost**: $1-3

### 7. Other Resources
- **KMS Key**: $1/month
- **SNS**: $0.10/month
- **EventBridge**: Free tier covers expected usage

## Cost Optimization Strategies

### 1. Conditional GuardDuty
```hcl
enable_guardduty = false  # Save $30-100/month
```
- Disable for cost savings
- Enable manually in console for demos
- Re-enable via Terraform when needed

### 2. Reduced Lambda Resources
```hcl
lambda_memory_size = 256   # Reduced from 512MB
lambda_timeout = 60        # Reduced from 300 seconds
```

### 3. Shorter Data Retention
```hcl
data_retention_days = 30           # Reduced from 90 days
cloudwatch_log_retention_days = 7  # Reduced from 14 days
```

### 4. S3 Lifecycle Management
- Standard storage: 0-30 days
- IA storage: 30-90 days
- Glacier: 90+ days (until deletion)

## Deployment Options

### Option 1: Cost-Optimized (Recommended for Portfolio)
```bash
terraform apply -var-file="terraform-cost-optimized.tfvars"
```
- **Monthly Cost**: ~$15-25
- **Functionality**: Core pipeline without GuardDuty
- **Demo Capability**: Full (can enable GuardDuty manually)

### Option 2: Full Featured
```bash
terraform apply -var-file="terraform.tfvars"
```
- **Monthly Cost**: ~$50-150
- **Functionality**: Complete with GuardDuty
- **Best For**: Full demonstration

### Option 3: Hybrid Approach
1. Deploy cost-optimized version
2. Enable GuardDuty manually for demos
3. Disable GuardDuty after demonstrations

## Manual Cost Controls

### 1. GuardDuty Management
```bash
# Enable for demo
aws guardduty create-detector --enable --profile johnadmin

# Disable after demo
aws guardduty delete-detector --detector-id <detector-id> --profile johnadmin
```

### 2. Lambda Monitoring
- Monitor invocation count in CloudWatch
- Adjust memory based on actual usage
- Set up billing alerts

### 3. S3 Storage Monitoring
- Review storage metrics monthly
- Adjust lifecycle rules if needed
- Monitor data transfer costs

## Billing Alerts Setup

### CloudWatch Billing Alert
```bash
# Create billing alarm for $20 threshold
aws cloudwatch put-metric-alarm \
  --alarm-name "AWS-Billing-Alert-20USD" \
  --alarm-description "Alert when charges exceed $20" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --threshold 20 \
  --comparison-operator GreaterThanThreshold \
  --profile johnadmin
```

## Portfolio Demonstration Strategy

### Phase 1: Deploy Cost-Optimized
- Deploy without GuardDuty
- Show core data pipeline functionality
- Demonstrate real-time processing

### Phase 2: Enable GuardDuty for Demo
- Manually enable GuardDuty
- Generate sample findings
- Show alert workflow

### Phase 3: Clean Up
- Disable GuardDuty after demo
- Keep core pipeline running
- Monitor costs weekly

## Expected Monthly Costs by Component

| Component | Cost-Optimized | Standard | Notes |
|-----------|----------------|----------|-------|
| Kinesis | $10.80 | $10.80 | Required |
| Lambda | $0.50-2 | $1-4 | Memory optimization |
| S3 | $1-5 | $2-10 | Lifecycle + retention |
| GuardDuty | $0 | $30-100 | Disabled vs enabled |
| CloudTrail | $2-5 | $2-5 | Management events free |
| CloudWatch | $0.50-1 | $1-3 | Reduced retention |
| KMS | $1 | $1 | Required |
| SNS | $0.10 | $0.10 | Minimal usage |
| **Total** | **$15-25** | **$50-150** | |

## Recommendations

1. **Start with cost-optimized configuration**
2. **Set up billing alerts at $20 and $50**
3. **Enable GuardDuty only for demos**
4. **Monitor actual usage weekly**
5. **Scale up resources only when needed**

This approach allows you to demonstrate full DevOps capabilities while maintaining minimal costs for portfolio development.
