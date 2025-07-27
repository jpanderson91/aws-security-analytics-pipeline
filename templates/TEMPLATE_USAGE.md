# Template Instantiation Instructions

## Quick Project Creation

### Create New Security Analytics Project
```powershell
# Navigate to templates directory
cd templates

# Create new security analytics project
.\New-AWSProject.ps1 -ProjectName "my-security-pipeline" -ProjectType "security-analytics" -TargetDirectory "C:\Projects"

# Navigate to new project
cd ..\my-security-pipeline

# Deploy infrastructure
cd terraform
terraform init
terraform apply -auto-approve
```

### Create New Data Pipeline Project
```powershell
# Create new data pipeline project
.\New-AWSProject.ps1 -ProjectName "my-data-pipeline" -ProjectType "data-pipeline" -OwnerName "Data Team"

# Follow quick start guide
cd ..\my-data-pipeline
cat QUICK_START.md
```

### Create New Web Application Project
```powershell
# Create new web application project
.\New-AWSProject.ps1 -ProjectName "my-web-app" -ProjectType "web-application" -CostCenter "Product"

# Review generated structure
cd ..\my-web-app
tree /f
```

## Available Project Types

| Project Type | Description | Basic Cost | Enterprise Cost | Deployment Time |
|-------------|-------------|------------|-----------------|-----------------|
| `security-analytics` | Security event processing and monitoring | $15/month | $100-200/month | 8-10 minutes |
| `data-pipeline` | ETL and data analytics platform | $20/month | $150-300/month | 10-12 minutes |
| `web-application` | Serverless web app with API backend | $10/month | $75-150/month | 6-8 minutes |

## Template Customization

### Adding New Project Types

1. **Edit New-AWSProject.ps1**
   - Add new configuration to `$ProjectConfigs` hashtable
   - Define service mappings and cost estimates

2. **Create Service-Specific Templates**
   - Add Terraform configurations for new services
   - Create appropriate test files
   - Update documentation templates

3. **Test New Template**
   ```powershell
   .\New-AWSProject.ps1 -ProjectName "test-project" -ProjectType "your-new-type"
   ```

### Modifying Existing Templates

1. **Update Template Files**
   - Modify files in `aws-project-template/`
   - Use `{{VARIABLE_NAME}}` for substitutions
   - Test with existing project types

2. **Add New Variables**
   - Update `$Replacements` hashtable in `New-AWSProject.ps1`
   - Add corresponding values to project configurations
   - Update template files with new variables

## Template Variables Reference

### Core Variables
- `{{PROJECT_NAME}}` - Name of the project
- `{{PROJECT_DESCRIPTION}}` - Detailed project description
- `{{PROJECT_TYPE}}` - Type of project (security-analytics, etc.)
- `{{OWNER_NAME}}` - Project owner name
- `{{COST_CENTER}}` - Billing cost center
- `{{DATE}}` - Current date

### Cost Variables
- `{{BASIC_COST}}` - Monthly cost for basic deployment
- `{{ENTERPRISE_COST}}` - Monthly cost for enterprise deployment
- `{{DEPLOYMENT_TIME}}` - Time to deploy in minutes

### Service Variables
- `{{PRIMARY_SERVICE}}` - Main AWS service
- `{{SECONDARY_SERVICE}}` - Supporting AWS service
- `{{STORAGE_SERVICE}}` - Storage service (S3, DynamoDB, etc.)
- `{{MONITORING_SERVICE}}` - Monitoring service (CloudWatch, etc.)

### Feature Variables
- `{{BASIC_FEATURES}}` - Features included in basic deployment
- `{{ENTERPRISE_FEATURES}}` - Additional enterprise features
- `{{SERVICE_COUNT}}` - Number of AWS services used

### Architecture Variables
- `{{ARCHITECTURE_TYPE}}` - Type of architecture pattern
- `{{TARGET_AUDIENCE}}` - Intended audience for the project
- `{{PROJECT_PURPOSE}}` - Business purpose of the project

## Best Practices

### Template Design
1. **Keep templates generic** - Use variables for all project-specific content
2. **Include comprehensive documentation** - README, QUICK_START, and technical docs
3. **Provide working examples** - Include test data and validation scripts
4. **Follow naming conventions** - Consistent file and resource naming
5. **Include cleanup instructions** - Always provide destruction/cleanup steps

### Variable Management
1. **Use descriptive variable names** - `{{PROJECT_NAME}}` not `{{NAME}}`
2. **Validate required variables** - Check for required parameters
3. **Provide sensible defaults** - Default to cost-optimized configurations
4. **Document all variables** - Include comments and descriptions

### Cost Optimization
1. **Default to basic tiers** - Use cost-optimized defaults
2. **Include cost estimates** - Provide realistic monthly cost projections
3. **Offer enterprise upgrades** - Separate basic and enterprise configurations
4. **Document scaling costs** - Explain cost implications of scaling

### Security Considerations
1. **Use IAM best practices** - Least privilege access
2. **Enable encryption by default** - Encrypt data at rest and in transit
3. **Include security checklists** - Provide security validation steps
4. **Sanitize sensitive data** - Remove account IDs and personal information

## Troubleshooting

### Common Issues

**Issue**: Template variables not being replaced
```powershell
# Solution: Check variable syntax in template files
# Ensure variables use {{VARIABLE_NAME}} format
```

**Issue**: Terraform validation errors in generated project
```powershell
# Solution: Test template with terraform validate
cd generated-project/terraform
terraform init
terraform validate
```

**Issue**: Missing files in generated project
```powershell
# Solution: Check template directory structure
# Ensure all required files are in aws-project-template/
```

### Validation Steps

1. **Test template generation**
   ```powershell
   .\New-AWSProject.ps1 -ProjectName "test" -ProjectType "security-analytics"
   ```

2. **Validate Terraform configuration**
   ```powershell
   cd test/terraform
   terraform init
   terraform validate
   terraform plan
   ```

3. **Check documentation**
   ```powershell
   cd ..
   cat README.md
   cat QUICK_START.md
   ```

4. **Cleanup test project**
   ```powershell
   cd ..
   Remove-Item -Path "test" -Recurse -Force
   ```

## Contributing

### Adding New Features

1. **Fork the template** - Create a copy for modification
2. **Test thoroughly** - Validate with multiple project types
3. **Document changes** - Update this file and project documentation
4. **Submit for review** - Include test results and examples

### Reporting Issues

1. **Include project type** - Specify which template type has issues
2. **Provide error messages** - Include full PowerShell or Terraform errors
3. **Share generated files** - Attach problematic generated files
4. **Describe expected behavior** - What should have happened instead
