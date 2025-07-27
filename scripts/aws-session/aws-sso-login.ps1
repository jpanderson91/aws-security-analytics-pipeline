# AWS SSO Login Script for Security Analytics Pipeline
# Provides extended session management with automatic verification

param(
    [switch]$Force,
    [switch]$Quiet
)

function Write-StatusMessage {
    param([string]$Message, [string]$Color = "White")
    if (-not $Quiet) {
        Write-Host $Message -ForegroundColor $Color
    }
}

function Start-AWSSecuritySession {
    Write-StatusMessage "🔐 Starting AWS SSO session for Security Analytics Pipeline..." "Cyan"

    # Check if already logged in (unless forced)
    if (-not $Force) {
        try {
            $identity = aws sts get-caller-identity --profile security-analytics 2>$null | ConvertFrom-Json
            if ($identity) {
                Write-StatusMessage "✅ Valid session already exists!" "Green"
                Write-StatusMessage "👤 User: $($identity.Arn.Split('/')[-1])" "Yellow"
                Write-StatusMessage "🏢 Account: $($identity.Account)" "Yellow"

                # Set environment variable
                $env:AWS_PROFILE = "security-analytics"
                return $true
            }
        }
        catch {
            # Session expired or invalid, continue to login
        }
    }

    # Login to SSO
    Write-StatusMessage "🔑 Initiating SSO login..." "Cyan"
    aws sso login --profile security-analytics

    if ($LASTEXITCODE -eq 0) {
        Write-StatusMessage "✅ SSO login successful!" "Green"

        # Verify identity
        try {
            $identity = aws sts get-caller-identity --profile security-analytics | ConvertFrom-Json
            Write-StatusMessage "👤 Logged in as: $($identity.Arn.Split('/')[-1])" "Yellow"
            Write-StatusMessage "🏢 Account: $($identity.Account)" "Yellow"
            Write-StatusMessage "🌍 Region: us-east-1" "Yellow"

            # Set as default profile for session
            $env:AWS_PROFILE = "security-analytics"
            Write-StatusMessage "🎯 AWS_PROFILE set to: security-analytics" "Green"

            # Quick infrastructure check
            Write-StatusMessage "🔍 Performing quick infrastructure check..." "Cyan"

            # Check Lambda functions
            $lambdas = aws lambda list-functions --query 'Functions[?contains(FunctionName, `security-analytics`)].FunctionName' --output text --profile security-analytics 2>$null
            if ($lambdas) {
                Write-StatusMessage "⚡ Found Lambda functions: $lambdas" "Green"
            }
            else {
                Write-StatusMessage "📝 No security-analytics Lambda functions found" "Yellow"
            }

            # Check Kinesis streams
            $streams = aws kinesis list-streams --query 'StreamNames[?contains(@, `security-analytics`)]' --output text --profile security-analytics 2>$null
            if ($streams) {
                Write-StatusMessage "🌊 Found Kinesis streams: $streams" "Green"
            }
            else {
                Write-StatusMessage "📝 No security-analytics Kinesis streams found" "Yellow"
            }

            Write-StatusMessage "🚀 Security Analytics Pipeline session ready!" "Green"
            return $true

        }
        catch {
            Write-StatusMessage "⚠️  Session verification failed: $($_.Exception.Message)" "Red"
            return $false
        }
    }
    else {
        Write-StatusMessage "❌ SSO login failed" "Red"
        Write-StatusMessage "💡 Check your SSO URL and try again" "Yellow"
        return $false
    }
}

# Main execution
$result = Start-AWSSecuritySession

if (-not $Quiet) {
    Write-Host ""
    Write-Host "🎯 Quick Commands:" -ForegroundColor Cyan
    Write-Host "  aws sts get-caller-identity                    # Check session" -ForegroundColor Gray
    Write-Host "  aws lambda list-functions                      # List Lambda functions" -ForegroundColor Gray
    Write-Host "  terraform init                                 # Initialize Terraform" -ForegroundColor Gray
    Write-Host "  terraform plan                                 # Plan infrastructure" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🔄 To refresh session: .\aws-sso-login.ps1 -Force" -ForegroundColor Cyan
    Write-Host "🔍 To check status: .\aws-session-check.ps1" -ForegroundColor Cyan
}

# Return success/failure for automation
exit $(if ($result) { 0 } else { 1 })
