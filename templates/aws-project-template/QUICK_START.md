# {{PROJECT_NAME}} - Quick Start Guide

> ⚡ **Deploy working AWS {{PROJECT_TYPE}} in {{DEPLOYMENT_TIME}} minutes**

## 🎯 **What You'll Get**

After following this guide, you'll have:
- ✅ **Live {{PROJECT_TYPE}}** processing real data
- ✅ **Working dashboards** with metrics and monitoring
- ✅ **Cost-optimized setup** (~${{BASIC_COST}}/month)
- ✅ **Portfolio-ready demonstration** with screenshots

---

## 📋 **Prerequisites (2 minutes)**

### Required Tools
```powershell
# Verify installations
aws --version          # AWS CLI v2 required
terraform --version    # Terraform 1.5+ required
python --version       # Python 3.8+ required
git --version          # Git for cloning
```

### AWS Configuration
```powershell
# Configure AWS credentials (choose one method)

# Method 1: AWS SSO (Recommended)
aws configure sso --profile {{PROJECT_NAME}}

# Method 2: AWS CLI configure
aws configure --profile {{PROJECT_NAME}}

# Verify access
aws sts get-caller-identity --profile {{PROJECT_NAME}}
```

---

## 🚀 **Deploy Infrastructure ({{DEPLOYMENT_TIME}} minutes)**

### Step 1: Clone and Setup
```powershell
# Clone repository
git clone {{REPO_URL}}
cd {{PROJECT_NAME}}

# Set AWS profile for session
$env:AWS_PROFILE = "{{PROJECT_NAME}}"
```

### Step 2: Deploy with Terraform
```powershell
# Navigate to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Review planned changes (optional)
terraform plan

# Deploy infrastructure
terraform apply -auto-approve
```

**Expected Output:**
```
Apply complete! Resources: {{RESOURCE_COUNT}} added, 0 changed, 0 destroyed.

Outputs:
dashboard_urls = {
  "{{DASHBOARD_1}}" = "https://{{REGION}}.console.aws.amazon.com/cloudwatch/home#dashboards:name={{DASHBOARD_NAME_1}}"
  "{{DASHBOARD_2}}" = "https://{{REGION}}.console.aws.amazon.com/cloudwatch/home#dashboards:name={{DASHBOARD_NAME_2}}"
}
```

### Step 3: Verify Deployment
```powershell
# Check {{PRIMARY_SERVICE}} status
{{VERIFICATION_COMMAND_1}}

# Check {{SECONDARY_SERVICE}} status
{{VERIFICATION_COMMAND_2}}

# View all resources
terraform output
```

---

## 🧪 **Test the System (3 minutes)**

### Generate Test Data
```powershell
# Navigate to testing directory
cd ../testing

# Install Python dependencies (if needed)
pip install -r requirements.txt

# Run end-to-end test
python test_{{PROJECT_TYPE}}.py
```

**Expected Results:**
```
✅ {{TEST_RESULT_1}}
✅ {{TEST_RESULT_2}}
✅ {{TEST_RESULT_3}}
✅ All tests passed - System is working correctly!
```

### View Live Dashboards
```powershell
# Get dashboard URLs
cd ../terraform
terraform output dashboard_urls

# Open dashboards in browser (copy URLs from output)
```

---

## 📊 **Portfolio Demonstration**

### Screenshots for Portfolio
1. **Main Dashboard**: Shows {{DASHBOARD_1_DESCRIPTION}}
2. **Metrics Dashboard**: Shows {{DASHBOARD_2_DESCRIPTION}}
3. **Cost Dashboard**: Shows resource costs and optimization

### Key Demonstration Points
- **Working Infrastructure**: Live metrics with zero errors
- **Cost Optimization**: ${{BASIC_COST}}/month operational cost
- **Professional Architecture**: {{ARCHITECTURE_HIGHLIGHTS}}
- **Security Best Practices**: {{SECURITY_HIGHLIGHTS}}

---

## 🔧 **Troubleshooting**

### Common Issues

**Issue**: `terraform apply` fails with permissions error
```powershell
# Solution: Verify AWS credentials
aws sts get-caller-identity --profile {{PROJECT_NAME}}

# Check required permissions
{{PERMISSION_CHECK_COMMAND}}
```

**Issue**: No data appearing in dashboards
```powershell
# Solution: Generate test data
cd testing
python test_{{PROJECT_TYPE}}.py

# Wait 2-3 minutes for data to appear
```

**Issue**: High costs in AWS
```powershell
# Solution: Check resource usage
{{COST_CHECK_COMMAND}}

# Clean up if needed
terraform destroy -auto-approve
```

### Get Help
- **Documentation**: See `/docs` directory
- **Issue Tracking**: Check `docs/ISSUE_TRACKING.md`
- **Architecture**: Review `docs/ARCHITECTURE.md`

---

## 🧹 **Cleanup (When Done)**

### Destroy Infrastructure
```powershell
# Navigate to terraform directory
cd terraform

# Destroy all resources
terraform destroy -auto-approve

# Verify cleanup
{{CLEANUP_VERIFICATION}}
```

**Expected Output:**
```
Destroy complete! Resources: {{RESOURCE_COUNT}} destroyed.
```

---

## 🎯 **Success Checklist**

After completing this guide, you should have:

- [ ] ✅ Infrastructure deployed successfully
- [ ] ✅ Test data flowing through system
- [ ] ✅ Dashboards showing live metrics
- [ ] ✅ Screenshots taken for portfolio
- [ ] ✅ Understanding of architecture
- [ ] ✅ Cleanup completed (if demo is done)

---

## 🚀 **Next Steps**

### For Portfolio
1. **Take Screenshots**: Capture working dashboards
2. **Document Experience**: Note any customizations made
3. **Update Resume**: Add {{PROJECT_TYPE}} and AWS services to skills

### For Enterprise Demo
1. **Deploy Enterprise Version**: See `enterprise-demo/` directory
2. **Enable Advanced Features**: Review enterprise configuration
3. **Cost Analysis**: Compare basic vs enterprise costs

### For Learning
1. **Explore Code**: Review `/src` directory implementation
2. **Study Terraform**: Examine infrastructure patterns
3. **Customize Features**: Modify and redeploy

---

**⏱️ Total Time**: {{DEPLOYMENT_TIME}} minutes
**💰 Cost**: ~${{BASIC_COST}}/month
**🎯 Result**: Production-ready {{PROJECT_TYPE}} with live dashboards

**Perfect for technical interviews, portfolio demonstrations, and AWS skills validation!**
