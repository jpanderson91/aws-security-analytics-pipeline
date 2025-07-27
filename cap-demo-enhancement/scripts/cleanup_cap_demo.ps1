# CAP Demo Complete Cleanup Script
# PowerShell script for complete infrastructure destruction

param(
    [Parameter(Mandatory = $false)]
    [switch]$Force,

    [Parameter(Mandatory = $false)]
    [switch]$SkipConfirmation
)

Write-Host "🧹 CAP Demo - Complete Environment Cleanup" -ForegroundColor Red
Write-Host "=" * 50

# Warning message
Write-Host ""
Write-Host "⚠️  WARNING: This will permanently delete:" -ForegroundColor Yellow
Write-Host "   • MSK Kafka cluster and all data" -ForegroundColor Yellow
Write-Host "   • ECS Fargate services and containers" -ForegroundColor Yellow
Write-Host "   • Lambda functions and logs" -ForegroundColor Yellow
Write-Host "   • S3 buckets and ALL stored data" -ForegroundColor Yellow
Write-Host "   • DynamoDB tables and metadata" -ForegroundColor Yellow
Write-Host "   • API Gateway endpoints" -ForegroundColor Yellow
Write-Host "   • CloudWatch dashboards and metrics" -ForegroundColor Yellow
Write-Host "   • All networking infrastructure (VPC, subnets, etc.)" -ForegroundColor Yellow

if (-not $SkipConfirmation) {
    $confirmation = Read-Host "`n🔥 Are you sure you want to proceed with complete cleanup? (yes/no)"
    if ($confirmation -ne "yes") {
        Write-Host "✅ Cleanup cancelled - no resources were deleted" -ForegroundColor Green
        exit 0
    }

    $finalConfirmation = Read-Host "🔥 FINAL CONFIRMATION: Type 'DELETE ALL' to proceed"
    if ($finalConfirmation -ne "DELETE ALL") {
        Write-Host "✅ Cleanup cancelled - no resources were deleted" -ForegroundColor Green
        exit 0
    }
}

# Check AWS credentials
Write-Host "`n🔑 Checking AWS credentials..." -ForegroundColor Cyan
try {
    $identity = aws sts get-caller-identity | ConvertFrom-Json
    Write-Host "✅ Connected as: $($identity.Arn)" -ForegroundColor Green
}
catch {
    Write-Host "❌ AWS credentials not available. Please run 'aws configure sso' first." -ForegroundColor Red
    exit 1
}

# Change to terraform directory
$terraformPath = Join-Path $PSScriptRoot "..\terraform"
if (-not (Test-Path $terraformPath)) {
    Write-Host "❌ Terraform directory not found: $terraformPath" -ForegroundColor Red
    exit 1
}

Set-Location $terraformPath
Write-Host "📁 Changed to terraform directory: $terraformPath" -ForegroundColor Cyan

# Empty S3 buckets first (required for deletion)
Write-Host "`n🗂️  Emptying S3 buckets..." -ForegroundColor Cyan
try {
    $buckets = aws s3api list-buckets --query 'Buckets[?contains(Name, `cap-demo`)].Name' --output text
    if ($buckets) {
        $bucketList = $buckets -split "`t"
        foreach ($bucket in $bucketList) {
            if ($bucket.Trim()) {
                Write-Host "   Emptying bucket: $bucket" -ForegroundColor Yellow
                aws s3 rm "s3://$bucket" --recursive --quiet
                Write-Host "   ✅ Emptied: $bucket" -ForegroundColor Green
            }
        }
    }
    else {
        Write-Host "ℹ️  No CAP demo S3 buckets found" -ForegroundColor Blue
    }
}
catch {
    Write-Host "⚠️  Warning: Could not empty some S3 buckets. Continuing..." -ForegroundColor Yellow
}

# Initialize Terraform
Write-Host "`n🏗️  Initializing Terraform..." -ForegroundColor Cyan
terraform init
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Terraform init failed" -ForegroundColor Red
    exit 1
}

# Run terraform destroy
Write-Host "`n🏗️  Running Terraform destroy..." -ForegroundColor Cyan
Write-Host "⏱️  This may take 10-15 minutes..." -ForegroundColor Yellow

$destroyStart = Get-Date
terraform destroy -auto-approve

if ($LASTEXITCODE -eq 0) {
    $destroyEnd = Get-Date
    $duration = $destroyEnd - $destroyStart
    Write-Host "`n✅ Terraform destroy completed successfully!" -ForegroundColor Green
    Write-Host "⏱️  Duration: $($duration.Minutes) minutes $($duration.Seconds) seconds" -ForegroundColor Green
}
else {
    Write-Host "`n❌ Terraform destroy failed. Attempting force cleanup..." -ForegroundColor Red

    # Try to destroy specific problematic resources
    $problematicResources = @(
        "aws_msk_cluster.main",
        "aws_ecs_service.event_processor",
        "aws_ecs_cluster.main",
        "aws_s3_bucket.bronze_data",
        "aws_s3_bucket.silver_data",
        "aws_s3_bucket.gold_data",
        "aws_vpc.main"
    )

    foreach ($resource in $problematicResources) {
        Write-Host "   Destroying $resource..." -ForegroundColor Yellow
        terraform destroy -target $resource -auto-approve
    }

    # Final destroy attempt
    Write-Host "🔄 Final cleanup attempt..." -ForegroundColor Cyan
    terraform destroy -auto-approve

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Some resources may still exist. Please check AWS console." -ForegroundColor Red
        Write-Host "💡 Manual cleanup may be required for:" -ForegroundColor Yellow
        Write-Host "   • S3 buckets with remaining objects" -ForegroundColor Yellow
        Write-Host "   • VPC with attached resources" -ForegroundColor Yellow
        Write-Host "   • Security groups with dependencies" -ForegroundColor Yellow
    }
}

# Verification
Write-Host "`n🔍 Verifying cleanup..." -ForegroundColor Cyan
try {
    $remainingVpcs = aws ec2 describe-vpcs --filters "Name=tag:Project,Values=cap-demo,CAP-Demo" --query 'Vpcs[].VpcId' --output text
    $remainingClusters = aws ecs list-clusters --query 'clusterArns[?contains(@, `cap`)]' --output text

    if ($remainingVpcs -or $remainingClusters) {
        Write-Host "⚠️  Some resources may still exist - check AWS console" -ForegroundColor Yellow
    }
    else {
        Write-Host "✅ Cleanup verification successful - no CAP demo resources found" -ForegroundColor Green
    }
}
catch {
    Write-Host "⚠️  Could not verify cleanup - please check AWS console manually" -ForegroundColor Yellow
}

# Final message
Write-Host "`n🎉 CAP Demo cleanup process completed!" -ForegroundColor Green
Write-Host "💰 Check AWS console to verify no resources are incurring costs" -ForegroundColor Green
Write-Host "📊 You can also check AWS Cost Explorer for cost validation" -ForegroundColor Cyan

# Generate timestamp for records
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
Write-Host "`n📄 Cleanup completed at: $timestamp" -ForegroundColor Cyan
Write-Host "💾 You may want to save this timestamp for cost tracking" -ForegroundColor Cyan
