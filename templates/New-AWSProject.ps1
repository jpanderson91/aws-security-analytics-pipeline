# Project Generation Script
# Use this to create new projects from templates

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectName,
    
    [Parameter(Mandatory=$true)]
    [string]$ProjectType,
    
    [Parameter(Mandatory=$false)]
    [string]$TargetDirectory = ".",
    
    [Parameter(Mandatory=$false)]
    [string]$OwnerName = "Development Team",
    
    [Parameter(Mandatory=$false)]
    [string]$CostCenter = "Engineering"
)

# Script configuration
$TemplateDir = Join-Path $PSScriptRoot "aws-project-template"
$OutputDir = Join-Path $TargetDirectory $ProjectName

Write-Host "🚀 Creating new AWS project: $ProjectName" -ForegroundColor Green
Write-Host "📁 Project Type: $ProjectType" -ForegroundColor Cyan
Write-Host "📂 Output Directory: $OutputDir" -ForegroundColor Yellow

# Project type configurations
$ProjectConfigs = @{
    "security-analytics" = @{
        PROJECT_DESCRIPTION = "Enterprise-grade security analytics pipeline for real-time threat detection and compliance monitoring"
        BASIC_COST = "15"
        ENTERPRISE_COST = "100-200"
        BASIC_FEATURES = "Kinesis Data Streams, Lambda Processing, S3 Storage, CloudWatch Dashboards"
        ENTERPRISE_FEATURES = "MSK Kafka, ECS Processing, QuickSight Analytics, Advanced Monitoring"
        PRIMARY_SERVICE = "Kinesis"
        SECONDARY_SERVICE = "Lambda"
        STORAGE_SERVICE = "S3"
        MONITORING_SERVICE = "CloudWatch"
        PROJECT_PURPOSE = "Security Analytics and Threat Detection"
        ARCHITECTURE_TYPE = "event-driven architecture"
        TARGET_AUDIENCE = "security teams and compliance officers"
        DEPLOYMENT_TIME = "8-10"
        SERVICE_COUNT = "6"
        BASIC_DESCRIPTION = "Real-time security event processing with automated threat detection"
        ENTERPRISE_DESCRIPTION = "Full enterprise security operations center simulation with advanced analytics"
    }
    
    "data-pipeline" = @{
        PROJECT_DESCRIPTION = "Scalable data processing pipeline with real-time analytics and machine learning capabilities"
        BASIC_COST = "20"
        ENTERPRISE_COST = "150-300"
        BASIC_FEATURES = "Kinesis Analytics, Lambda ETL, S3 Data Lake, Athena Queries"
        ENTERPRISE_FEATURES = "EMR Spark, SageMaker ML, Redshift Analytics, DataSync"
        PRIMARY_SERVICE = "Kinesis Analytics"
        SECONDARY_SERVICE = "Lambda"
        STORAGE_SERVICE = "S3"
        MONITORING_SERVICE = "CloudWatch"
        PROJECT_PURPOSE = "Data Processing and Analytics"
        ARCHITECTURE_TYPE = "data lake architecture"
        TARGET_AUDIENCE = "data engineers and analysts"
        DEPLOYMENT_TIME = "10-12"
        SERVICE_COUNT = "8"
        BASIC_DESCRIPTION = "ETL pipeline with automated data processing and basic analytics"
        ENTERPRISE_DESCRIPTION = "Enterprise data platform with ML capabilities and advanced analytics"
    }
    
    "web-application" = @{
        PROJECT_DESCRIPTION = "Modern serverless web application with API Gateway, authentication, and database integration"
        BASIC_COST = "10"
        ENTERPRISE_COST = "75-150"
        BASIC_FEATURES = "API Gateway, Lambda Functions, DynamoDB, CloudFront CDN"
        ENTERPRISE_FEATURES = "ECS Fargate, RDS Aurora, ElastiCache, Cognito Auth"
        PRIMARY_SERVICE = "API Gateway"
        SECONDARY_SERVICE = "Lambda"
        STORAGE_SERVICE = "DynamoDB"
        MONITORING_SERVICE = "CloudWatch"
        PROJECT_PURPOSE = "Web Application Development"
        ARCHITECTURE_TYPE = "serverless architecture"
        TARGET_AUDIENCE = "development teams and product managers"
        DEPLOYMENT_TIME = "6-8"
        SERVICE_COUNT = "5"
        BASIC_DESCRIPTION = "Serverless web app with API backend and database"
        ENTERPRISE_DESCRIPTION = "Enterprise web platform with advanced features and scaling"
    }
}

# Get project configuration
if (-not $ProjectConfigs.ContainsKey($ProjectType)) {
    Write-Error "Unknown project type: $ProjectType. Available types: $($ProjectConfigs.Keys -join ', ')"
    exit 1
}

$Config = $ProjectConfigs[$ProjectType]

# Create output directory
if (Test-Path $OutputDir) {
    Write-Warning "Directory $OutputDir already exists. Contents may be overwritten."
    $response = Read-Host "Continue? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Operation cancelled." -ForegroundColor Red
        exit 0
    }
} else {
    New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null
}

# Copy template files
Write-Host "📋 Copying template files..." -ForegroundColor Cyan
Copy-Item -Path "$TemplateDir\*" -Destination $OutputDir -Recurse -Force

# Define template replacements
$Replacements = @{
    "{{PROJECT_NAME}}" = $ProjectName
    "{{PROJECT_DESCRIPTION}}" = $Config.PROJECT_DESCRIPTION
    "{{BASIC_COST}}" = $Config.BASIC_COST
    "{{ENTERPRISE_COST}}" = $Config.ENTERPRISE_COST
    "{{BASIC_FEATURES}}" = $Config.BASIC_FEATURES
    "{{ENTERPRISE_FEATURES}}" = $Config.ENTERPRISE_FEATURES
    "{{PRIMARY_SERVICE}}" = $Config.PRIMARY_SERVICE
    "{{SECONDARY_SERVICE}}" = $Config.SECONDARY_SERVICE
    "{{STORAGE_SERVICE}}" = $Config.STORAGE_SERVICE
    "{{MONITORING_SERVICE}}" = $Config.MONITORING_SERVICE
    "{{PROJECT_PURPOSE}}" = $Config.PROJECT_PURPOSE
    "{{ARCHITECTURE_TYPE}}" = $Config.ARCHITECTURE_TYPE
    "{{TARGET_AUDIENCE}}" = $Config.TARGET_AUDIENCE
    "{{DEPLOYMENT_TIME}}" = $Config.DEPLOYMENT_TIME
    "{{SERVICE_COUNT}}" = $Config.SERVICE_COUNT
    "{{BASIC_DESCRIPTION}}" = $Config.BASIC_DESCRIPTION
    "{{ENTERPRISE_DESCRIPTION}}" = $Config.ENTERPRISE_DESCRIPTION
    "{{OWNER_NAME}}" = $OwnerName
    "{{COST_CENTER}}" = $CostCenter
    "{{DATE}}" = (Get-Date -Format "yyyy-MM-dd")
    "{{PROJECT_TYPE}}" = $ProjectType
}

# Process template files
Write-Host "🔄 Processing template variables..." -ForegroundColor Cyan

$FilesToProcess = Get-ChildItem -Path $OutputDir -Recurse -File | Where-Object { 
    $_.Extension -in @('.md', '.tf', '.py', '.json', '.yaml', '.yml', '.ps1', '.sh') 
}

foreach ($File in $FilesToProcess) {
    Write-Host "  Processing: $($File.Name)" -ForegroundColor Gray
    
    $Content = Get-Content -Path $File.FullName -Raw
    
    foreach ($Key in $Replacements.Keys) {
        $Content = $Content -replace [regex]::Escape($Key), $Replacements[$Key]
    }
    
    Set-Content -Path $File.FullName -Value $Content -NoNewline
}

# Create additional project-specific directories
Write-Host "📁 Creating project structure..." -ForegroundColor Cyan

$AdditionalDirs = @(
    "docs\screenshots",
    "src\$($Config.PRIMARY_SERVICE.ToLower())",
    "src\$($Config.SECONDARY_SERVICE.ToLower())",
    "testing\integration",
    "scripts\deployment",
    "archive",
    ".github\workflows"
)

foreach ($Dir in $AdditionalDirs) {
    $DirPath = Join-Path $OutputDir $Dir
    New-Item -Path $DirPath -ItemType Directory -Force | Out-Null
}

# Create .gitignore
$GitIgnoreContent = @"
# Terraform
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl
*.tfplan
.terraformrc
terraform.rc

# AWS
.aws/
*.pem
credentials

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/

# IDE
.vscode/settings.json
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Project specific
config/local.json
secrets/
*.backup
archive/temp/
testing/output/
"@

Set-Content -Path (Join-Path $OutputDir ".gitignore") -Value $GitIgnoreContent

# Create basic project documentation
Write-Host "📝 Creating project documentation..." -ForegroundColor Cyan

# Create initial project status
$ProjectStatusContent = @"
# $ProjectName - Project Status

## Overview
- **Project Type**: $ProjectType
- **Created**: $(Get-Date -Format "yyyy-MM-dd")
- **Owner**: $OwnerName
- **Cost Center**: $CostCenter

## Status
- [ ] Infrastructure deployed
- [ ] Basic testing completed
- [ ] Dashboards configured
- [ ] Documentation complete
- [ ] Portfolio screenshots taken

## Architecture
- **Primary Service**: $($Config.PRIMARY_SERVICE)
- **Secondary Service**: $($Config.SECONDARY_SERVICE)
- **Storage**: $($Config.STORAGE_SERVICE)
- **Monitoring**: $($Config.MONITORING_SERVICE)

## Cost Targets
- **Basic Deployment**: $($Config.BASIC_COST)/month
- **Enterprise Deployment**: $($Config.ENTERPRISE_COST)/month

## Next Steps
1. Review and customize Terraform configuration
2. Deploy infrastructure using QUICK_START.md
3. Run end-to-end tests
4. Configure monitoring dashboards
5. Take portfolio screenshots
"@

Set-Content -Path (Join-Path $OutputDir "docs\PROJECT_STATUS.md") -Value $ProjectStatusContent

Write-Host "✅ Project creation completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Project Location: $OutputDir" -ForegroundColor Yellow
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. cd '$OutputDir'" -ForegroundColor White
Write-Host "  2. Review and customize terraform/variables.tf" -ForegroundColor White
Write-Host "  3. Follow QUICK_START.md for deployment" -ForegroundColor White
Write-Host "  4. See docs/PROJECT_STATUS.md for checklist" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Project Type: $ProjectType" -ForegroundColor Green
Write-Host "💰 Estimated Cost: $($Config.BASIC_COST)/month (basic) | $($Config.ENTERPRISE_COST)/month (enterprise)" -ForegroundColor Green
Write-Host "⏱️  Deployment Time: $($Config.DEPLOYMENT_TIME) minutes" -ForegroundColor Green
