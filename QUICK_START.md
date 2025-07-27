# ⚡ **Quick Start Guide**

> Get the AWS Security Analytics Pipeline running in **10 minutes** or less!

## 🎯 **What You'll Build**

A complete security analytics pipeline that:
- ✅ Processes real security events in AWS
- ✅ Stores data in a partitioned S3 data lake
- ✅ Provides live CloudWatch dashboards
- ✅ Costs less than $15/month to run

## 📋 **Prerequisites** (2 minutes)

```bash
# Verify required tools
aws --version          # AWS CLI v2
terraform --version    # Terraform 1.5+
python --version       # Python 3.8+

# Configure AWS credentials
aws configure sso
aws sts get-caller-identity
```

## 🚀 **Deploy** (5 minutes)

```bash
# Clone and setup
git clone https://github.com/jpanderson91/aws-security-analytics-pipeline.git
cd aws-security-analytics-pipeline/terraform

# Deploy infrastructure
terraform init
terraform apply -auto-approve
```

## ✅ **Test** (3 minutes)

```bash
# Generate test events
cd ../testing
python test_pipeline.py

# Verify resources
aws lambda list-functions --query 'Functions[?contains(FunctionName, `security-analytics`)]'
aws kinesis list-streams --query 'StreamNames[?contains(@, `security-analytics`)]'

# Get dashboard URLs
cd ../terraform
terraform output dashboard_urls
```

## 🎉 **Success!**

You should now have:
- ✅ **Lambda function** processing events
- ✅ **Kinesis stream** ingesting data
- ✅ **S3 bucket** storing processed events
- ✅ **CloudWatch dashboards** showing live metrics

## 🎯 **What's Next?**

### 📊 **View Your Dashboards**
Open the URLs from `terraform output` to see your live metrics.

### 🏢 **Try Enterprise Features**
Explore the [Enterprise Demo](cap-demo-enhancement/) for advanced MSK Kafka and ECS features.

### 🧹 **Clean Up**
```bash
cd terraform
terraform destroy -auto-approve
```

## 🆘 **Troubleshooting**

| Issue | Solution |
|-------|----------|
| **"No credentials"** | Run `aws configure sso` |
| **Terraform errors** | Check `terraform --version` >= 1.5 |
| **Lambda not found** | Wait 2-3 minutes for deployment |
| **No dashboard data** | Run `python test_pipeline.py` |

**Need help?** Check the [complete troubleshooting guide](docs/ISSUE_TRACKING.md).

---

**⏱️ Total Time**: 10 minutes
**💰 Monthly Cost**: ~$15
**🎯 Perfect for**: Portfolio demos, interviews, proof-of-concept
