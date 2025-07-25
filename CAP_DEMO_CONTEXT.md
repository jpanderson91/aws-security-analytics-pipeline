# CAP Demo Project - Conversation Summary & Setup Guide

**Date**: July 25, 2025  
**Project**: Toyota CAP-Style Data Ingestion Platform Demo  
**Goal**: Build Portfolio Project 2 for Senior AWS Data DevOps Engineer Interview

## 🎯 **Project Context**

### **Completed Foundation (Project 1)**
- ✅ AWS Security Analytics Pipeline - COMPLETE
- ✅ Kinesis → Lambda → S3 pipeline working
- ✅ Professional CloudWatch dashboards
- ✅ Zero errors, 138ms processing time
- ✅ Cost optimized: $15-25/month

### **Project 2 Goal (CAP Demo)**
Replicate Toyota CAP team architecture:
```
Customer On-Prem → Beats Agents (MSI) → MSK Kafka → ECS/Lambda → S3 (Bronze/Silver/Gold) → Logstash → Sentinel
```

### **Key Requirements from POC Proposal**
- MSK Kafka cluster management
- ECS migration showcase (EC2 → ECS)
- Bronze/Silver/Gold data pipeline
- JDBC connector simulation
- Customer onboarding workflows

## 🚀 **Implementation Plan**

### **Weekend Strategy (Accelerated)**
- **Saturday**: MSK Kafka foundation + ECS setup (4-6 hours)
- **Sunday**: Data pipeline + Demo scenarios (5-7 hours)
- **Total Cost**: ~$50-60 for weekend

### **Phase Breakdown**
1. **MSK Kafka Foundation** - Core CAP infrastructure
2. **ECS Migration Demo** - Show EC2 → ECS benefits  
3. **Bronze/Silver/Gold Pipeline** - Data layer processing
4. **Customer Scenarios** - JIRA workflow simulation

## 🛠️ **Technical Setup Completed**

### **IDE Configuration Files Created**
- VS Code settings optimized for Terraform + Python + Kafka
- Debug configurations for CAP components
- Build tasks for MSK, ECS, data pipeline
- Multi-folder workspace setup

### **Dependencies Identified**
```
# Core for CAP Demo
boto3==1.34.131
kafka-python==2.0.2
confluent-kafka==2.2.0
pandas==2.0.3
docker==6.1.3
terraform (CLI tool)
```

### **Project Structure Designed**
```
cap-data-ingestion-demo/
├── terraform/
│   ├── msk.tf                    # MSK Kafka cluster
│   ├── ecs.tf                    # ECS services
│   ├── s3-data-layers.tf         # Bronze/Silver/Gold buckets
│   └── main.tf                   # Core infrastructure
├── src/
│   ├── data-processor/           # ECS container application
│   ├── jdbc-connectors/          # Customer database integration
│   ├── beats-configs/            # Customer MSI configurations
│   └── pipeline/                 # Bronze → Silver → Gold processing
├── customer-scenarios/
│   ├── setup_customer_ingestion.py
│   ├── deploy_jdbc_connector.py
│   └── simulate_jira_workflow.py
└── docs/
```

## 🔧 **Setup Instructions for New Device**

### **Step 1: Prerequisites**
```powershell
# Verify tools (run in PowerShell as Admin)
python --version          # Should be >= 3.8
pip --version
terraform --version       # Should be >= 1.0
docker --version
aws --version             # AWS CLI v2

# Configure AWS
aws configure --profile cap-demo
# Enter: Access Key, Secret Key, Region (us-east-1 for MSK)
```

### **Step 2: Project Setup**
```powershell
# Create project directory
mkdir C:\cap-data-ingestion-demo
cd C:\cap-data-ingestion-demo

# Create directory structure
mkdir terraform, src\lambda\processors, src\ecs\data-processor, src\kafka\connectors, docker, scripts\demo-scenarios, configs\beats, configs\jdbc, docs, testing, .vscode

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Copy configuration files (from exported files)
# - settings.json → .vscode\
# - tasks.json → .vscode\
# - launch.json → .vscode\
# - requirements.txt → root
# - test_environment.py → root

# Install dependencies
pip install -r requirements.txt

# Test environment
python test_environment.py
```

### **Step 3: Begin Implementation**
Start with MSK Kafka cluster setup (terraform/msk.tf)

## 📊 **Demo Scenarios to Build**

### **Scenario 1: New Customer JIRA Ticket**
```python
# Simulate: "Setup data ingestion for Customer ABC"
python setup_customer_ingestion.py --customer="abc-corp" --data-type="windows-events"
# Creates Kafka topic, Beats config, monitoring
```

### **Scenario 2: JDBC Connector**
```python
# Database connection with Secrets Manager
python deploy_jdbc_connector.py --customer="xyz-corp" --database-type="mssql"
```

### **Scenario 3: ECS Migration**
```bash
# Show EC2 → ECS benefits
terraform apply -target=aws_ecs_service.data_processor
```

### **Scenario 4: Data Pipeline**
```python
# Bronze → Silver → Gold processing
# Raw CloudTrail → S3 interactions only → 3-month aggregations
```

## 🎯 **Interview Value Proposition**

This demo will showcase:
- **Kafka Administration** (core CAP skill)
- **ECS Orchestration** (current CAP migration)
- **Multi-tier Data Processing** (Bronze/Silver/Gold)
- **Customer Onboarding Workflows** (real CAP scenarios)
- **Enterprise Data Pipeline Design**

## 🔄 **Resume Point**

When you resume on your personal computer:
1. Copy all configuration files from current workspace
2. Set up the project structure and environment
3. Test with `python test_environment.py`
4. Begin with **MSK Kafka cluster setup** (Phase 1)

## 💡 **Key Technical Decisions Made**

- **Output Format**: JSON (CAP compatibility)
- **Cost Strategy**: MSK t3.small instances, minimal storage
- **Architecture**: Extending proven Project 1 patterns
- **Tools**: Terraform + Python + Docker + AWS CLI

---

**Next Conversation Starter**: "I'm ready to continue the CAP demo project from where we left off. I have the environment set up and want to begin with the MSK Kafka cluster foundation."
