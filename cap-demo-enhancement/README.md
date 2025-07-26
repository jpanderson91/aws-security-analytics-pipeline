# Cloud Analytics Platform (CAP)

🛡️ **Enterprise-grade security analytics pipeline for real-time threat detection and compliance monitoring**

## 🎯 Overview

The CAP (Cloud Analytics Platform) demonstrates a complete AWS-native security analytics solution that ingests, processes, and analyzes security events in real-time. This pipeline showcases modern data engineering patterns, serverless architectures, and advanced analytics capabilities.

### 🏗️ Architecture Highlights

- **Real-time Event Ingestion**: Apache Kafka (MSK) for high-throughput data streaming
- **Scalable Processing**: ECS Fargate containers for event processing and enrichment
- **Data Lake Architecture**: S3-based Bronze/Silver/Gold data tiering
- **Serverless Analytics**: Lambda functions for real-time event processing
- **Customer APIs**: API Gateway endpoints for secure data access
- **Business Intelligence**: QuickSight dashboards for security metrics visualization
- **Infrastructure as Code**: Terraform for complete resource provisioning

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- Terraform >= 1.0
- Python 3.9+
- Docker (for local development)

### 1. Environment Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure AWS SSO (recommended)
aws configure sso
```

### 2. Phase-by-Phase Deployment

```bash
# Phase 1: Data Ingestion (Kafka/MSK)
python scripts/setup_phase1_kafka.py

# Phase 2: Data Processing (ECS/Lambda)
python scripts/setup_phase2_processing.py

# Phase 3: Analytics & APIs (QuickSight/API Gateway)
python scripts/setup_phase3_analytics.py
```

### 3. Validation & Testing

```bash
# Run complete validation
python scripts/run_complete_validation.py

# Test end-to-end flow
python scripts/run_full_demo.py
```

## 📁 Project Structure

```
cap-security-analytics-pipeline/
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md         # Technical architecture
│   ├── DEPLOYMENT_GUIDE.md     # Detailed deployment guide
│   ├── DEMO_SCRIPT.md          # Demo recording script
│   └── screenshots/            # Architecture diagrams & screenshots
├── terraform/                  # Infrastructure as Code
│   ├── main.tf                 # Main Terraform configuration
│   ├── variables.tf            # Input variables
│   ├── outputs.tf              # Output values
│   └── dashboards.tf           # QuickSight dashboard configuration
├── src/                        # Application source code
│   ├── lambda/                 # Lambda function code
│   │   └── event_processor/    # Event processing Lambda
│   └── deploy.py               # Deployment utilities
├── scripts/                    # Automation scripts
│   ├── setup_phase1_kafka.py         # Phase 1 deployment
│   ├── setup_phase2_processing.py    # Phase 2 deployment
│   ├── setup_phase3_analytics.py     # Phase 3 deployment
│   ├── verify_phase*.py              # Phase validation scripts
│   ├── run_complete_validation.py    # Complete validation runner
│   ├── run_full_demo.py              # Demo orchestration
│   └── produce_security_events.py    # Test data generation
└── tests/                      # Testing scripts
    ├── test_phase2_dataflow.py        # Data flow testing
    └── test_customer_apis.py          # API testing
```

## 🔧 Core Components

### Phase 1: Data Ingestion
- **Amazon MSK**: Managed Kafka cluster for event streaming
- **Security Groups**: Network isolation and access control
- **Topic Management**: Automated Kafka topic creation and configuration

### Phase 2: Data Processing
- **ECS Fargate**: Containerized event processors
- **AWS Lambda**: Real-time event processing functions
- **S3 Data Lake**: Bronze/Silver/Gold data architecture
- **AWS Glue**: Data catalog and ETL jobs

### Phase 3: Analytics & APIs
- **Amazon Athena**: Serverless SQL analytics
- **Amazon QuickSight**: Business intelligence dashboards
- **API Gateway**: RESTful APIs for data access
- **DynamoDB**: Customer metadata storage

## 🎭 Demo Scenarios

The pipeline includes three demonstration scenarios:

1. **Security Incident Response**: Real-time threat detection and alerting
2. **Customer Onboarding**: New customer data integration flow
3. **Real-time Analytics**: Live security metrics and dashboards

## 📊 Key Features

- ✅ **Real-time Processing**: Sub-second event processing and alerting
- ✅ **Scalable Architecture**: Auto-scaling based on demand
- ✅ **Cost Optimized**: Serverless and spot instance utilization
- ✅ **Security First**: IAM roles, VPC isolation, encryption at rest/transit
- ✅ **Monitoring**: CloudWatch metrics and custom dashboards
- ✅ **DevOps Ready**: Infrastructure as Code with Terraform

## 💰 Cost Optimization

The pipeline is designed for cost efficiency:
- Serverless Lambda for event processing
- ECS Spot instances for batch processing
- S3 Intelligent Tiering for storage optimization
- MSK provisioned throughput scaling

Expected monthly cost: **$50-150** (depending on data volume)

## 🔍 Monitoring & Observability

- **CloudWatch Dashboards**: Real-time metrics and alarms
- **Custom Metrics**: Business KPIs and operational metrics
- **Distributed Tracing**: End-to-end request tracking
- **Log Aggregation**: Centralized logging with search capabilities

## 🤝 Contributing

This project demonstrates enterprise-grade AWS security analytics capabilities. For questions or discussions about the architecture and implementation decisions, please review the documentation in the `docs/` directory.

## 📄 License

This project is available under the MIT License. See the LICENSE file for details.

---

**Built with ❤️ using AWS native services and modern data engineering practices**
