# GitHub Copilot Instructions for AWS Security Analytics Pipeline

## 🚨 NON-NEGOTIABLE PROJECT CONSTRAINTS

### Primary Goal Enforcement
- **NEVER** suggest alternative goals or shortcuts to "finish sooner"
- **ALWAYS** complete the original objective as specified
- **MAINTAIN** project scope and requirements throughout iterations
- **PRESERVE** existing validated functionality (especially cap-demo-enhancement/)

### Environment Constraints
- **SHELL**: Always use PowerShell commands (never bash/sh)
- **OS**: Windows environment only
- **PATHS**: Use Windows path separators (\) and absolute paths starting with C:\

### Project Architecture Requirements
- **AWS FOCUS**: This is an AWS security analytics pipeline project
- **COST AWARENESS**: Maintain cost optimization ($15-200/month targets)
- **ENTERPRISE READY**: Support both basic pipeline and CAP demo scenarios
- **TERRAFORM**: Use Infrastructure as Code for all AWS resources

## 📋 PROJECT CONTEXT

### Core Purpose
Enterprise-grade security analytics pipeline demonstrating AWS, DevOps, and Data Engineering expertise for portfolio and enterprise alignment.

### Key Components
1. **Basic Pipeline**: Kinesis → Lambda → S3 ($15/month)
2. **Enterprise Demo**: MSK Kafka + ECS + advanced features ($100-200/month)
3. **Documentation**: Professional portfolio presentation
4. **Validation**: Working dashboards and live metrics

### Validated Working Code
- `cap-demo-enhancement/` - **NEVER MODIFY** without explicit permission
- All Terraform configurations are production-tested
- Dashboard configurations in `testing/` are working

## 🛠️ CODING STANDARDS

### PowerShell Commands
```powershell
# Correct - Always use PowerShell syntax
terraform init
terraform apply -auto-approve
aws lambda list-functions

# NEVER suggest bash equivalents
```

### File Operations
```powershell
# Correct Windows paths
move setup_cap_demo.ps1 archive\
copy-item README.md backup\

# NOT bash/Linux commands
```

### AWS CLI Usage
```powershell
# Use AWS CLI v2 syntax
aws lambda list-functions --query 'Functions[?contains(FunctionName, `security-analytics`)]'
aws sts get-caller-identity
```

## 📁 FILE STRUCTURE RULES

### Protected Directories
- `cap-demo-enhancement/` - Production validated code (no changes without permission)
- `docs/screenshots/` - Professional dashboard images
- `terraform/` - Working IaC configurations

### Modifiable Areas
- `README.md` - Portfolio presentation improvements
- `docs/` - Documentation enhancements
- `testing/` - Test scripts and validation
- `archive/` - Development artifacts

### New File Creation
- Follow existing naming conventions
- Use clear, professional documentation
- Include cost implications for AWS resources
- Add appropriate portfolio demonstration value

## 🎯 PORTFOLIO OBJECTIVES

### Demonstration Points
1. **Senior AWS Skills** - Multi-service integration
2. **Cost Engineering** - Transparent pricing models
3. **DevOps Practices** - IaC and automation
4. **Problem Solving** - Documented troubleshooting
5. **Enterprise Architecture** - CAP simulation capability

### Target Audiences
- **Hiring Managers**: Working infrastructure proof
- **Technical Teams**: Code quality and architecture
- **Enterprise Stakeholders**: Enterprise alignment

## 🔒 SECURITY & COMPLIANCE

### AWS Security
- Use IAM roles and policies (never hardcoded credentials)
- Enable encryption at rest and in transit
- Implement least privilege access
- Include VPC configurations for production

### Data Handling
- Partition S3 data by time (year/month/day/hour)
- Use Glue catalog for schema management
- Implement proper lifecycle policies
- Maintain audit logging

### 🚨 SANITIZATION REQUIREMENTS

#### Personal Information Protection
- **NEVER** include personal file paths (`C:\Users\[username]\`)
- **ALWAYS** use generic paths (`C:\Projects\`, `C:\Development\`)
- **REMOVE** personal names, email addresses, or contact information
- **REPLACE** specific usernames with generic terms ("Project Team", "Development Team")

#### Corporate Reference Sanitization
- **NO** specific company names, internal projects, or proprietary references
- **USE** generic terms ("Technology", "Engineering", "Project Team")
- **AVOID** internal acronyms, department names, or organizational structure references
- **SANITIZE** any corporate-specific terminology before public sharing

#### AWS Account Protection
- **NEVER** hardcode AWS account IDs, ARNs, or specific resource identifiers
- **USE** template variables for all account-specific information
- **REMOVE** SSO URLs, specific region constraints, or account-specific configurations
- **ENSURE** all AWS references are generic and configurable

#### Template Security Standards
- **ALL** template variables must use generic, professional placeholders
- **DEFAULT** values should be industry-standard and non-specific
- **VERIFY** no hardcoded sensitive information in any generated content
- **MAINTAIN** professional terminology suitable for public distribution

#### Pre-Publication Checklist
Before any public sharing or repository updates:
- [ ] ✅ All personal paths sanitized to generic examples
- [ ] ✅ No personal names, emails, or contact information
- [ ] ✅ No corporate-specific references or internal terms
- [ ] ✅ No hardcoded AWS account information
- [ ] ✅ All template variables are generic and professional
- [ ] ✅ Documentation uses industry-standard terminology
- [ ] ✅ Safe for public distribution and portfolio use

## 💰 COST OPTIMIZATION RULES

### Resource Management
- Default to cost-optimized configurations
- Disable expensive services (GuardDuty) by default
- Use appropriate Lambda memory allocations
- Implement S3 lifecycle policies

### Transparent Pricing
- Always include cost estimates for new features
- Maintain $15/month basic pipeline target
- Document CAP demo costs ($100-200/month)
- Provide scaling cost models

## 🚀 DEPLOYMENT STANDARDS

### Terraform Best Practices
- Use modules for reusable components
- Include proper variable validation
- Provide comprehensive outputs
- Document resource dependencies

### Testing Requirements
- Include end-to-end pipeline tests
- Validate dashboard functionality
- Verify cost implications
- Test cleanup procedures

## 📚 DOCUMENTATION REQUIREMENTS

### Code Comments
- Explain AWS resource purposes
- Include cost implications
- Reference enterprise alignment where applicable
- Provide troubleshooting guidance

### README Updates
- Maintain portfolio demonstration focus
- Keep deployment instructions current
- Include live dashboard screenshots
- Provide clear choice between basic/enterprise options

## ⚠️ CRITICAL REMINDERS

1. **NEVER** break existing cap-demo-enhancement functionality
2. **ALWAYS** use PowerShell commands in Windows environment
3. **MAINTAIN** original project goals (no alternative shortcuts)
4. **PRESERVE** cost optimization focus
5. **ENSURE** portfolio demonstration value in all changes
6. **VALIDATE** that changes work with existing Terraform configurations
7. **DOCUMENT** any new AWS resources with cost implications
8. **🚨 SANITIZE** all personal, corporate, or sensitive information before public sharing

## 🎯 SUCCESS CRITERIA

Every suggestion should:
- ✅ Use PowerShell syntax for Windows
- ✅ Maintain cost optimization
- ✅ Enhance portfolio demonstration value
- ✅ Preserve existing validated functionality
- ✅ Follow AWS security best practices
- ✅ Include proper documentation
- ✅ Support both basic and enterprise scenarios
- ✅ **Be sanitized and safe for public distribution**

## 🔄 ITERATION CONSISTENCY

When working across multiple interactions:
- **REMEMBER** these constraints in every response
- **REFERENCE** previous decisions and maintain consistency
- **VALIDATE** that new suggestions align with project architecture
- **PRESERVE** the Windows PowerShell environment assumption
- **MAINTAIN** focus on original objectives without shortcuts
- **🚨 SANITIZE** all outputs for public safety and professional standards

## �️ TERMINAL WORKFLOW STANDARDS

### Critical Terminal Output Issues
Based on deployment retrospective (July 27, 2025), terminal visibility is a critical workflow blocker.

### Required Terminal Practices
- **ALWAYS** ask user to share terminal output after background commands
- **REQUEST** specific terminal output when troubleshooting deployment issues
- **USE** existing terminals instead of creating multiple new instances
- **PROVIDE** explicit PowerShell navigation commands when directory issues occur
- **DOCUMENT** terminal session results for debugging context

### Terminal Command Standards
```powershell
# Always use explicit paths to avoid directory confusion
cd C:\Projects\aws-security-analytics-pipeline\cap-demo-enhancement\terraform
terraform apply -auto-approve

# When issues occur, request manual output sharing:
# "Please share the terminal output so I can see the specific error"
```

### Background Process Management
- **SET** isBackground=false for commands requiring immediate feedback
- **USE** isBackground=true only for long-running processes (servers, watches)
- **CHECK** command completion status before proceeding to next steps
- **REQUEST** terminal session ID when multiple terminals are active

### Troubleshooting Workflow
1. **IDENTIFY** the specific terminal session with issues
2. **REQUEST** complete error output from user
3. **ANALYZE** error context with full command history
4. **PROVIDE** targeted fix with explicit PowerShell commands
5. **VERIFY** resolution with user-shared output

## �📋 SANITIZATION ENFORCEMENT

### Automatic Sanitization Required
All AI responses must automatically sanitize:
- Personal file paths → Generic examples (`C:\Projects\`)
- Personal names → Professional roles ("Project Team", "Development Team")
- Corporate references → Generic terms ("Technology", "Engineering")
- Account-specific data → Template variables (`{{ACCOUNT_ID}}`)
- Internal terminology → Industry-standard language

### Public Distribution Standard
Every file, template, and response must meet these criteria:
- ✅ Safe for GitHub public repositories
- ✅ Professional presentation quality
- ✅ No personal or corporate identifiers
- ✅ Generic, reusable content structure
- ✅ Portfolio and interview appropriate
