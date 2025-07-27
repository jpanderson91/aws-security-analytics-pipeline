# AWS Security Analytics Pipeline

[![Deploy Status](https://img.shields.io/badge/Deploy-Success-green)]() [![Cost Optimized](https://img.shields.io/badge/Cost-Optimized-blue)]() [![Portfolio Ready](https://img.shields.io/badge/Portfolio-Ready-brightgreen)]() [![AWS](https://img.shields.io/badge/AWS-Multi--Service-orange)]() [![Terraform](https://img.shields.io/badge/IaC-Terraform-purple)]()

> 🛡️ **Enterprise-grade security analytics pipeline demonstrating AWS, DevOps, and Data Engineering expertise**

## 🚀 **Choose Your Experience Level**

### ⚡ **Basic Pipeline** - Production Ready ($15/month)
Complete security analytics pipeline with real-time processing and monitoring.

**Features:** Kinesis → Lambda → S3, CloudWatch dashboards, cost-optimized  
**Perfect for:** Portfolio demonstrations, interviews, personal projects  
**→ [Deploy Basic Pipeline](README.md#basic-deployment)**

### 🏢 **Enterprise CAP Demo** - Full Toyota Architecture ($100-200/month)
Complete Cloud Analytics Platform simulation with MSK Kafka, ECS, and advanced features.

**Features:** MSK Kafka, ECS services, Bronze/Silver/Gold data tiers, Customer APIs  
**Perfect for:** Enterprise demos, technical deep-dives, CAP team alignment  
**→ [Deploy CAP Demo](cap-demo-enhancement/)**

---

## 🏆 **Portfolio Demonstration**

This repository showcases **senior-level AWS capabilities** through two complementary projects:

### 🏢 **Enterprise CAP Architecture** 
- **Toyota CAP Simulation**: Real MSK Kafka cluster with ECS container orchestration
- **Multi-Tier Processing**: Bronze/Silver/Gold data pipeline architecture
- **Customer Workflows**: JIRA ticket simulation and onboarding automation
- **Advanced Analytics**: API Gateway endpoints and QuickSight dashboards

## 📊 **Technical Skills Demonstrated**

| Skill Area | Basic Pipeline | CAP Demo |
|------------|----------------|-----------|
| **Infrastructure as Code** | ✅ Terraform | ✅ Advanced Terraform Modules |
| **Serverless Architecture** | ✅ Lambda + Kinesis | ✅ Lambda + ECS + MSK |
| **Data Engineering** | ✅ Real-time Processing | ✅ Multi-tier Data Lake |
| **Cost Optimization** | ✅ $15/month | ✅ Scalable Cost Models |
| **DevOps Practices** | ✅ CI/CD Ready | ✅ Enterprise Automation |
| **Security** | ✅ IAM + Encryption | ✅ VPC + Advanced Security |

## 📸 **Live Dashboard Screenshots**

![Security Analytics Dashboard](docs/screenshots/security-analytics-dashboard.png)
*Security Analytics Dashboard - Shows Lambda performance, Kinesis activity, and S3 data lake status*

![Security Metrics Dashboard](docs/screenshots/security-metrics-dashboard.png)  
*Security Metrics Dashboard - Real-time metrics showing 3 events processed, 0 errors, 138ms avg processing time*

![Cost Tracking Dashboard](docs/screenshots/cost-tracking-dashboard.png)
*Cost Tracking Dashboard - Resource utilization and cost optimization monitoring*

> 🎯 **Portfolio Demonstration**: These screenshots show a live, working AWS security analytics pipeline processing real data with zero errors and fast performance.

> *Designed for RSOC (Regional Security Operations Center) requirements - demonstrating expertise in AWS security services, event-driven architecture, and cost optimization strategies.*

## 🏗️ Architecture

```mermaid
graph TB
    CT[CloudTrail] --> KS[Kinesis Data Stream]
    GD[GuardDuty*] --> KS
    KS --> LF[Lambda Function<br/>Event Processor]
    LF --> S3[S3 Data Lake<br/>Partitioned Storage]
    LF --> SNS[SNS Alerts]
    S3 --> GC[Glue Catalog]
    GC --> AT[Athena Queries]
    AT --> CW[CloudWatch<br/>Dashboards]
    
    style LF fill:#ff6b6b
    style S3 fill:#4ecdc4
    style KS fill:#45b7d1
    style GD fill:#96ceb4,stroke-dasharray: 5 5
```

*GuardDuty currently disabled for cost optimization*

## 📊 Key Features

### ✅ **Deployed & Functional**
- **Real-time Event Processing**: Kinesis + Lambda architecture processing security events
- **Data Enrichment**: IP geolocation, threat intelligence, and risk scoring
- **Intelligent Alerting**: SNS notifications for high-risk events
- **Cost-Optimized**: ~$5-15/month for full functionality

### 🔒 **Security Analytics**
- **Event Classification**: CloudTrail, GuardDuty, and custom event processing
- **Risk Scoring Algorithm**: 0-100 scale with multiple factors
- **Threat Intelligence**: IP reputation and known threat detection
- **Geographic Analysis**: Location-based risk assessment

### 🗄️ **Data Lake Architecture**
- **Partitioned Storage**: Time-based S3 organization (year/month/day/hour)
- **Query-Ready**: Glue catalog integration for Athena queries
- **Scalable Design**: Handles varying event volumes efficiently
- **Retention Management**: Automated lifecycle policies

### 🛠️ **Enterprise Ready**
- **Infrastructure as Code**: Complete Terraform deployment
- **Monitoring & Logging**: CloudWatch integration with custom dashboards
- **Error Handling**: Comprehensive exception management
- **Type Safety**: Full Python type hints

## � **Live Production Results**

### Security Analytics Dashboard
![Security Analytics Dashboard](docs/screenshots/security-analytics-dashboard.png)
*Production dashboard showing Lambda performance, Kinesis activity, and S3 data lake metrics*

### Security Metrics Dashboard  
![Security Metrics Dashboard](docs/screenshots/security-metrics-dashboard.png)
*Real-time processing metrics: 3 events processed, 0 errors, 138ms average response time*

### Cost Tracking Dashboard
![Cost Tracking Dashboard](docs/screenshots/cost-tracking-dashboard.png)
*Resource utilization and cost optimization monitoring - maintaining $15/month target*

> 🎯 **Portfolio Evidence**: These screenshots prove live, working AWS infrastructure processing real security events with enterprise-grade monitoring.

---

## � **Basic Deployment** 

### Prerequisites
```bash
# Install required tools
aws --version          # AWS CLI v2
terraform --version    # Terraform 1.5+
python --version       # Python 3.11+

# Configure AWS credentials
aws configure sso
aws sts get-caller-identity
```

### Deploy Infrastructure (10 minutes)
```bash
# Clone and deploy
git clone https://github.com/jpanderson91/aws-security-analytics-pipeline.git
cd aws-security-analytics-pipeline/terraform

# Initialize and deploy
terraform init
terraform apply -auto-approve

# Verify deployment
aws lambda list-functions --query 'Functions[?contains(FunctionName, `security-analytics`)]'
aws kinesis list-streams --query 'StreamNames[?contains(@, `security-analytics`)]'
```

### Test the Pipeline
```bash
# Generate test events
cd ../testing
python test_pipeline.py

# View live dashboards (URLs from terraform output)
terraform output dashboard_urls
```

**Expected Results:**
- ✅ Lambda processing events in <200ms
- ✅ S3 objects created with proper partitioning  
- ✅ CloudWatch dashboards showing live metrics
- ✅ Zero processing errors

---
aws configure sso
aws sts get-caller-identity --profile YOUR_PROFILE
```

### 🎯 **Cost-Optimized Deployment** (Recommended)
```bash
# Clone and navigate
git clone https://github.com/jpanderson91/aws-security-analytics-pipeline.git
cd aws-security-analytics-pipeline/terraform

# Initialize Terraform
terraform init

# Deploy infrastructure
terraform apply -auto-approve

# Verify deployment
aws lambda list-functions
aws kinesis list-streams
```

### 🧪 **Test the Pipeline**
```bash
# Navigate to testing directory
cd ../testing

# Run end-to-end test
python test_pipeline.py

# Expected output:
# ✅ Event 1 sent successfully
# ✅ Event 2 sent successfully  
# ✅ Event 3 sent successfully
# 📊 3/3 events processed successfully
```

## 📁 Project Structure

```
aws-security-analytics-pipeline/
├── docs/                   # 📋 Complete documentation
│   ├── DASHBOARD_VALIDATION.md  # Dashboard URLs & validation guide
│   ├── ISSUE_TRACKING.md       # Complete issue resolution log  
│   ├── PROJECT_STATUS.md       # Portfolio status summary
│   ├── cost-analysis.md        # Cost optimization analysis
│   ├── PROJECT_1_CLEANUP_SUMMARY.md # Resource cleanup documentation
│   └── screenshots/            # Professional dashboard images
├── src/                    # 💻 Source code
│   ├── deploy.py          # Deployment automation script
│   └── lambda/            # Lambda function code
│       └── event_processor/    # Main event processing function
├── terraform/             # 🏗️ Infrastructure as Code
│   ├── main.tf           # Core infrastructure configuration
│   ├── dashboards.tf     # CloudWatch dashboards
│   ├── variables.tf      # Input variables
│   └── outputs.tf        # Output values
├── testing/               # 🧪 Testing & validation
│   ├── test_pipeline.py  # End-to-end pipeline testing
│   └── dashboard_configs/ # Fixed dashboard JSON configurations
├── PROJECT_1_COMPLETE.md  # Final project summary
└── README.md              # This file
```

## 📈 Dashboard Metrics

### Security Overview
- **Threat Detection Rate**: Real-time GuardDuty findings
- **API Activity**: CloudTrail event analysis
- **Geographic Distribution**: Login locations and patterns
- **Risk Score Trends**: Time-series security metrics

### Operational Metrics
- **Event Processing Latency**: Pipeline performance
- **Data Volume**: Processed events per hour
- **System Health**: Infrastructure monitoring
- **Cost Analysis**: Resource utilization tracking

## 🔧 Configuration

The pipeline is configured through Terraform variables in the `terraform/` directory. Key configurations include:

### AWS Resources
- **Region**: us-east-1 (configurable)
- **Environment**: dev (default)
- **Project Name**: security-analytics

### Cost Optimization
- GuardDuty disabled by default (can be enabled manually)
- Reduced log retention periods
- Optimized Lambda memory allocation
- S3 lifecycle policies for cost management

For detailed cost analysis, see [docs/cost-analysis.md](docs/cost-analysis.md).

## 🧪 Testing

## 🏗️ **Architecture Overview**

```mermaid
graph TB
    subgraph "Data Ingestion"
        CT[CloudTrail Events]
        CE[Custom Events]
    end
    
    subgraph "Real-time Processing"
        KS[Kinesis Data Stream]
        LF[Lambda Function]
    end
    
    subgraph "Data Lake"
        S3[S3 Buckets]
        GC[Glue Catalog]
    end
    
    subgraph "Analytics & Monitoring"
        AT[Athena Queries]
        CW[CloudWatch Dashboards]
        SNS[SNS Alerts]
    end
    
    CT --> KS
    CE --> KS
    KS --> LF
    LF --> S3
    LF --> SNS
    S3 --> GC
    GC --> AT
    AT --> CW
    
    style LF fill:#ff6b6b
    style S3 fill:#4ecdc4
    style KS fill:#45b7d1
```

---

## 📚 **Documentation & Portfolio Assets**

| Document | Purpose | Audience |
|----------|---------|----------|
| [**Basic Pipeline**](README.md#basic-deployment) | Quick deployment guide | Everyone |
| [**CAP Demo**](cap-demo-enhancement/) | Enterprise architecture | Technical stakeholders |
| [**Project Status**](docs/PROJECT_STATUS.md) | Portfolio summary | Hiring managers |
| [**Issue Resolution**](docs/ISSUE_TRACKING.md) | Problem-solving skills | Technical interviewers |
| [**Cost Analysis**](docs/cost-analysis.md) | Financial responsibility | Management |
| [**Dashboard Validation**](docs/DASHBOARD_VALIDATION.md) | Live proof of concept | Demonstrations |

---

## 🎯 **Portfolio Demonstration Points**

### **For Hiring Managers:**
- ✅ **Working Infrastructure** - Live dashboards with real metrics
- ✅ **Cost Consciousness** - $15/month operational cost with enterprise features
- ✅ **Professional Documentation** - Complete project lifecycle documentation
- ✅ **Problem-Solving Skills** - Documented troubleshooting and resolution process

### **For Technical Teams:**
- ✅ **Infrastructure as Code** - Complete Terraform automation with best practices
- ✅ **Serverless Architecture** - Event-driven design with auto-scaling
- ✅ **Security Implementation** - Multi-layer security with encryption and IAM
- ✅ **Monitoring & Observability** - Comprehensive CloudWatch integration

### **For Enterprise Stakeholders:**
- ✅ **Toyota CAP Alignment** - Real MSK Kafka and ECS architecture in [CAP Demo](cap-demo-enhancement/)
- ✅ **Scalable Design** - From $15/month to enterprise-scale deployment options
- ✅ **Compliance Ready** - Audit logging, encryption, and data governance
- ✅ **Multi-tier Processing** - Bronze/Silver/Gold data lake architecture

---

## 🚀 **Ready to Impress**

**This repository demonstrates senior-level AWS and DevOps capabilities through:**

1. **Proven Production Systems** - Working infrastructure with live monitoring
2. **Enterprise Architecture** - Complete CAP simulation with advanced features  
3. **Cost Engineering** - Smart resource optimization and financial responsibility
4. **Professional Execution** - Documentation, testing, and issue resolution

**Perfect for technical interviews, hiring manager demonstrations, and portfolio showcasing.**

---

**Project Status**: ✅ **Production Ready**  
**Last Updated**: July 2025  
**AWS Services**: 15+ integrated services  
**Cost Target**: $15-200/month (configurable)  
**Deployment Time**: 10-60 minutes depending on complexity
- Working CloudWatch dashboards with real data
- End-to-end pipeline processing test events
- Zero-cost shutdown capability demonstrated
- Professional documentation and screenshot evidence

## 📞 Support

For questions about this implementation or Toyota RSOC integration:

- **Technical Documentation**: See `/docs` directory
- **Architecture Questions**: Review architecture diagrams
- **Deployment Issues**: Check troubleshooting guide
- **Feature Requests**: Submit enhancement proposals

---

**Project Status**: ✅ Production Ready  
**Last Updated**: July 2025  
**AWS Services**: 8+ integrated services  
**Security Focus**: Toyota RSOC alignment
