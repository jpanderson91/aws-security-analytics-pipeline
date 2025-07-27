# PowerShell Profile Enhancement for AWS Security Analytics Pipeline
# Add this content to your PowerShell profile for automatic AWS session management

# AWS Security Analytics Pipeline Environment Setup
function Initialize-SecurityAnalyticsEnvironment {
    Write-Host "🛡️ AWS Security Analytics Pipeline Environment" -ForegroundColor Cyan

    # Set default AWS profile
    $env:AWS_PROFILE = "security-analytics"
    $env:AWS_DEFAULT_REGION = "us-east-1"

    # Check if we're in the project directory
    $projectPath = "C:\Users\jpand\sec-analytics-pipeline\aws-security-analytics-pipeline-4"
    if (Test-Path $projectPath) {
        # Create helpful aliases
        function aws-login { & "$projectPath\scripts\aws-session\aws-sso-login.ps1" }
        function aws-check { & "$projectPath\scripts\aws-session\aws-session-check.ps1" }
        function aws-status { & "$projectPath\scripts\aws-session\aws-session-check.ps1" -Detailed }
        function aws-refresh { & "$projectPath\scripts\aws-session\aws-sso-login.ps1" -Force }

        # Project navigation aliases
        function cdp { Set-Location $projectPath }
        function cdpt { Set-Location "$projectPath\terraform" }
        function cdps { Set-Location "$projectPath\src" }
        function cdpd { Set-Location "$projectPath\docs" }
        function cdpc { Set-Location "$projectPath\cap-demo-enhancement" }

        # Quick commands
        function tf-init {
            Push-Location "$projectPath\terraform"
            terraform init
            Pop-Location
        }
        function tf-plan {
            Push-Location "$projectPath\terraform"
            terraform plan
            Pop-Location
        }
        function tf-apply {
            Push-Location "$projectPath\terraform"
            terraform apply
            Pop-Location
        }

        Write-Host "✅ AWS Security Analytics environment loaded!" -ForegroundColor Green
        Write-Host "🔧 Available commands:" -ForegroundColor Yellow
        Write-Host "   aws-login, aws-check, aws-status, aws-refresh" -ForegroundColor Gray
        Write-Host "   cdp (project), cdpt (terraform), cdps (src), cdpd (docs)" -ForegroundColor Gray
        Write-Host "   tf-init, tf-plan, tf-apply" -ForegroundColor Gray
    }
}

# Auto-check AWS session on profile load
function Test-AWSSessionQuick {
    try {
        $identity = aws sts get-caller-identity --profile security-analytics 2>$null | ConvertFrom-Json
        if ($identity) {
            Write-Host "🔐 AWS Session Active: $($identity.Arn.Split('/')[-1])@$($identity.Account)" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️  No AWS session - run 'aws-login' to authenticate" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "⚠️  No AWS session - run 'aws-login' to authenticate" -ForegroundColor Yellow
    }
}

# Initialize environment
Initialize-SecurityAnalyticsEnvironment

# Quick session check (only if not in ISE or other special environments)
if ($Host.Name -eq "ConsoleHost") {
    Test-AWSSessionQuick
}

# Custom prompt with AWS status
function prompt {
    $awsStatus = ""
    if ($env:AWS_PROFILE) {
        try {
            $identity = aws sts get-caller-identity --profile $env:AWS_PROFILE 2>$null | ConvertFrom-Json
            if ($identity) {
                $awsStatus = " [AWS:✅]"
            }
            else {
                $awsStatus = " [AWS:❌]"
            }
        }
        catch {
            $awsStatus = " [AWS:❌]"
        }
    }

    "PS $(Get-Location)$awsStatus> "
}

Write-Host "`n🎯 PowerShell profile loaded with AWS Security Analytics Pipeline extensions!" -ForegroundColor Cyan
