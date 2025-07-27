# AWS Project Templates System

This directory contains reusable templates for rapidly creating professional AWS portfolio projects.

## Quick Start

```powershell
# Create a new security analytics project
.\New-AWSProject.ps1 -ProjectName "my-security-pipeline" -ProjectType "security-analytics"

# Create a new data pipeline project
.\New-AWSProject.ps1 -ProjectName "my-data-pipeline" -ProjectType "data-pipeline"

# Create a new web application project
.\New-AWSProject.ps1 -ProjectName "my-web-app" -ProjectType "web-application"
```

## Available Templates

| Template | Cost | Deploy Time | Services | Purpose |
|----------|------|-------------|----------|---------|
| **security-analytics** | $15-200/month | 8-10 min | Kinesis, Lambda, S3, CloudWatch | Security event processing and monitoring |
| **data-pipeline** | $20-300/month | 10-12 min | Kinesis Analytics, Lambda, S3, Athena | ETL and data analytics platform |
| **web-application** | $10-150/month | 6-8 min | API Gateway, Lambda, DynamoDB, CloudFront | Serverless web application |

## Template Features

✅ **Production Ready** - Working infrastructure with live monitoring
✅ **Cost Optimized** - Smart defaults with enterprise scaling options
✅ **Portfolio Ready** - Professional documentation and screenshots
✅ **Security First** - IAM best practices and encryption by default
✅ **Rapid Deployment** - 6-12 minute setup with automated testing

## 🏗️ **Repository Structure Templates**

This directory contains templates for quickly spinning up well-organized project repositories based on lessons learned from the AWS Security Analytics Pipeline project evolution.

## 📋 **Available Templates**

### 1. **AWS Project Template** (`aws-project-template/`)
Complete structure for AWS infrastructure projects with:
- Terraform IaC organization
- Multi-environment support (dev/staging/prod)
- Security best practices
- Cost optimization frameworks
- Documentation standards

### 2. **Portfolio Project Template** (`portfolio-project/`)
Professional repository structure optimized for:
- Hiring manager demonstrations
- Technical interviews
- Public portfolio showcasing
- Enterprise presentation

### 3. **Enterprise Demo Template** (`enterprise-demo/`)
Advanced project structure for enterprise-scale demonstrations:
- Multiple deployment scenarios
- Advanced feature showcases
- Professional documentation
- Cost transparency

## 🚀 **Quick Start**

```powershell
# Generate new project from template
.\scripts\create-project-from-template.ps1 -TemplateName "aws-project" -ProjectName "my-new-project" -ProjectPath "C:\Users\jpand\projects\"

# Available templates:
# - aws-project: Standard AWS infrastructure project
# - portfolio-project: Portfolio demonstration project
# - enterprise-demo: Enterprise-scale demonstration
```

## 📁 **Template Structure Evolution**

Based on our AWS Security Analytics Pipeline iterations:

### **Iteration 1**: Basic project structure
- ❌ **Issues**: Files scattered, unclear navigation, duplicate content

### **Iteration 2**: Repository cleanup
- ✅ **Improvements**: Archive system, better organization
- ❌ **Remaining**: Manual organization, no standardization

### **Iteration 3**: Template system (this)
- ✅ **Solutions**: Automated structure, consistent patterns, reusable templates

## 🎯 **Template Benefits**

### **Time Savings**
- **Project Setup**: 2-3 hours → 15 minutes
- **Documentation**: Pre-written professional templates
- **Structure**: Consistent organization from day one

### **Quality Assurance**
- **Security**: Built-in security checklists and patterns
- **Documentation**: Professional README and portfolio standards
- **Best Practices**: Terraform, AWS, and DevOps patterns included

### **Consistency**
- **Portfolio**: Uniform presentation across projects
- **Enterprise**: Standard enterprise demonstration patterns
- **Maintenance**: Predictable structure for updates

## 📚 **Usage Scenarios**

### **New AWS Project**
```powershell
.\create-project-from-template.ps1 -TemplateName "aws-project" -ProjectName "serverless-api"
```

### **Portfolio Addition**
```powershell
.\create-project-from-template.ps1 -TemplateName "portfolio-project" -ProjectName "data-pipeline-demo"
```

### **Enterprise Demo**
```powershell
.\create-project-from-template.ps1 -TemplateName "enterprise-demo" -ProjectName "microservices-platform"
```

## 🛠️ **Customization**

Each template includes:
- **Variable substitution**: `{{PROJECT_NAME}}`, `{{AUTHOR}}`, `{{DATE}}`
- **Modular components**: Choose features to include/exclude
- **Environment-specific**: Dev, staging, production configurations
- **Security defaults**: Pre-configured security best practices

## 📖 **Template Documentation**

See individual template directories for:
- Complete README templates
- Directory structure explanations
- Configuration examples
- Deployment guides
- Best practices documentation
