# Operations Guide
## AWS Security Analytics Pipeline

## 🎯 **Overview**
This guide consolidates all operational knowledge for managing, troubleshooting, and maintaining the AWS Security Analytics Pipeline. It serves as the single source of truth for day-to-day operations.

---

## 🔑 **AWS Authentication & Session Management**

### **SSO Configuration**
The project uses AWS SSO with the `security-analytics` profile. For extended sessions:

**Enhanced AWS Config (`~/.aws/config`):**
```ini
[profile security-analytics]
sso_session = security-analytics
sso_account_id = {{YOUR_AWS_ACCOUNT_ID}}
sso_role_name = AdministratorAccess
region = us-east-1
cli_pager =
output = json

[sso-session security-analytics]
sso_start_url = https://{{YOUR_SSO_DOMAIN}}.awsapps.com/start/#
sso_region = us-east-1
sso_registration_scopes = sso:account:access
sso_max_attempts = 3
sso_cli_max_attempts = 3
```

### **Session Management Commands**
```powershell
# Login to AWS SSO
aws sso login --profile security-analytics

# Check current session
aws sts get-caller-identity --profile security-analytics

# Refresh expired session
aws sso logout --profile security-analytics
aws sso login --profile security-analytics
```

### **Session Duration Factors**
- **AWS SSO Admin Settings**: 1-12 hours (configured in AWS SSO console)
- **Client Token Cache**: AWS CLI caches tokens locally
- **Role Session Duration**: Individual role temporary credentials (15min - 12 hours)

---

## 🚨 **Common Issues & Troubleshooting**

### **1. Terminal Output Visibility Issues**
**Problem:** AI agents or scripts can't see terminal output reliably
**Solution:**
- Always request manual terminal output sharing for debugging
- Use explicit PowerShell navigation commands
- Avoid multiple background processes simultaneously

### **2. VPC Configuration Errors**
**Problem:** Security groups and subnets reference incorrect VPC IDs
**Symptoms:**
- `InvalidGroup.NotFound` errors
- `InvalidSubnetID.NotFound` errors

**Solution:**
```hcl
# Use resource references, not variables
vpc_security_group_ids = [aws_security_group.ecs_sg.id]
subnet_ids = aws_subnet.private[*].id
# NOT: var.vpc_id or var.private_subnet_ids
```

### **3. Lambda VPC Configuration**
**Problem:** `SubnetIds and SecurityIds must coexist or be both empty list`
**Solution:** Ensure both VPC security groups AND subnets are properly configured:
```hcl
vpc_config {
  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.lambda_sg.id]
}
```

### **4. MSK Authentication Issues**
**Problem:** MSK cluster updates fail with "no updates to security setting"
**Solution:** For demo environments, use unauthenticated access:
```hcl
client_authentication {
  unauthenticated = true
}
# Remove empty TLS blocks
```

### **5. ALB Access Logs Permission Denied**
**Problem:** S3 bucket permission error for ALB access logs
**Solution:** Create proper S3 bucket policy for ELB service account:
```hcl
data "aws_elb_service_account" "main" {}

resource "aws_s3_bucket_policy" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id
  policy = jsonencode({
    Statement = [{
      Effect = "Allow"
      Principal = { AWS = data.aws_elb_service_account.main.arn }
      Action = "s3:PutObject"
      Resource = "${aws_s3_bucket.alb_logs.arn}/*"
    }]
  })
}
```

### **6. API Gateway CloudWatch Logging**
**Problem:** CloudWatch Logs role ARN not set in account settings
**Solution:** Create account-level API Gateway CloudWatch role:
```hcl
resource "aws_api_gateway_account" "main" {
  cloudwatch_role_arn = aws_iam_role.api_gateway_cloudwatch.arn
}
```

### **7. Resource Limits**
**Problem:** Hit EIP allocation limits, NAT gateway limits
**Solution:**
- Check AWS service limits before deployment
- Use single NAT gateway for cost optimization in demo environments
- Clean up unused EIPs in the account

---

## 📊 **Dashboard Troubleshooting**

### **"No Data Available" in CloudWatch Dashboards**
**Root Causes:**
1. **No Real Event Data**: Pipeline deployed but no test events processed
2. **Dashboard Configuration**: Incorrect widget configurations
3. **Metric Timing**: CloudWatch metrics have inherent delays

**Solutions:**
1. **Generate Test Events:**
   ```powershell
   cd cap-demo-enhancement
   python scripts/produce_security_events.py
   ```

2. **Verify Lambda Invocations:**
   ```powershell
   aws lambda list-functions --query 'Functions[?contains(FunctionName, `security-analytics`)]'
   aws lambda invoke --function-name dev-cap-demo-analytics-trigger response.json
   ```

3. **Check S3 Data Flow:**
   ```powershell
   aws s3 ls s3://dev-cap-demo-bronze-data/year=$(Get-Date -Format yyyy)/month=$(Get-Date -Format MM)/day=$(Get-Date -Format dd)/
   ```

### **Empty API Gateway Metrics**
**Cause:** No API requests made
**Solution:** Test API endpoints:
```powershell
# Get API Gateway URL
$api_url = (aws apigateway get-rest-apis --query 'items[0].name' --output text)

# Test endpoints
Invoke-RestMethod -Uri "$api_url/dev/metrics" -Method GET
Invoke-RestMethod -Uri "$api_url/dev/security" -Method GET
```

---

## 🏗️ **Deployment Procedures**

### **Standard Deployment Workflow**
```powershell
# 1. Navigate to terraform directory
cd cap-demo-enhancement/terraform

# 2. Initialize Terraform
terraform init

# 3. Plan deployment
terraform plan

# 4. Apply changes
terraform apply -auto-approve

# 5. Validate deployment
cd ../scripts
python run_complete_validation.py
```

### **Cleanup Procedures**
```powershell
# Destroy infrastructure
cd cap-demo-enhancement/terraform
terraform destroy -auto-approve

# Verify cleanup
aws lambda list-functions --query 'Functions[?contains(FunctionName, `cap-demo`)]'
aws ecs list-clusters --query 'clusterArns[?contains(@, `cap-demo`)]'
```

---

## 📈 **Monitoring & Validation**

### **Health Check Commands**
```powershell
# Check all major services
aws ecs list-clusters --query 'clusterArns[?contains(@, `cap-demo`)]'
aws lambda list-functions --query 'Functions[?contains(FunctionName, `cap-demo`)]'
aws kafka list-clusters --query 'ClusterInfoList[?ClusterName==`cap-demo-cluster`]'
aws apigateway get-rest-apis --query 'items[?name==`cap-demo-api`]'
```

### **Cost Monitoring**
- **Target Costs**: $15/month basic, $100-200/month enterprise demo
- **Key Cost Drivers**: MSK cluster, ECS tasks, Lambda invocations, data transfer
- **Optimization**: Use single AZ for demo, minimize data retention periods

### **Performance Baselines**
- **Lambda Cold Start**: < 5 seconds
- **API Response Time**: < 2 seconds
- **Event Processing**: < 30 seconds end-to-end
- **Dashboard Refresh**: < 60 seconds for new data

---

## 🔧 **Maintenance Tasks**

### **Weekly Tasks**
- Check CloudWatch dashboards for anomalies
- Review AWS costs in Cost Explorer
- Validate all services are running
- Check S3 storage usage and lifecycle policies

### **Monthly Tasks**
- Review and archive old process documentation
- Update operational procedures with new lessons learned
- Validate backup and recovery procedures
- Review security configurations

### **Quarterly Tasks**
- Comprehensive cost optimization review
- Update Terraform modules to latest versions
- Review and update documentation structure
- Validate disaster recovery procedures

---

## 📚 **References & Links**

### **Key Documentation**
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Current project state
- [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) - Security validation procedures
- [cost-analysis.md](cost-analysis.md) - Detailed cost breakdown and optimization

### **External Resources**
- [AWS SSO Documentation](https://docs.aws.amazon.com/singlesignon/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS CLI Reference](https://docs.aws.amazon.com/cli/latest/reference/)

### **Emergency Contacts**
- AWS Support: [Support Center](https://console.aws.amazon.com/support/)
- Project Documentation: [GitHub Repository](https://github.com/jpanderson91/aws-security-analytics-pipeline)

---

## 📝 **Change Log**
- **2025-07-27**: Initial consolidation of operational knowledge
- **Next Update**: Quarterly review scheduled for 2025-10-27
