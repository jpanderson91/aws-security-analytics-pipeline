# AWS SSO Extended Session Configuration and Management
# For AWS Security Analytics Pipeline Project

## � SECURITY NOTICE
**Before using these scripts:**
1. Replace `YOUR_AWS_ACCOUNT_ID` with your actual AWS account ID
2. Replace `YOUR_SSO_DOMAIN` with your actual SSO domain
3. Never commit actual AWS account IDs or SSO URLs to public repositories
4. Keep your `~/.aws/config` and `~/.aws/credentials` files private

## �🔑 **SSO Session Duration Extension Guide**

### **Current Configuration Enhanced**
Your AWS config has been set up with the `security-analytics` profile. To extend session duration, we need to:

1. **Configure SSO Session Cache Duration** (Client-side)
2. **Set up Automatic Session Refresh**
3. **Create Session Management Scripts**

## 🛠️ **Enhanced AWS Configuration**

### **1. Extended SSO Session Configuration**

Add these settings to your `~/.aws/config` file:

```ini
[profile security-analytics]
sso_session = security-analytics
sso_account_id = YOUR_AWS_ACCOUNT_ID
sso_role_name = AdministratorAccess
region = us-east-1
cli_pager =
output = json

[sso-session security-analytics]
sso_start_url = https://YOUR_SSO_DOMAIN.awsapps.com/start/#
sso_region = us-east-1
sso_registration_scopes = sso:account:access
# Extended session configuration
sso_max_attempts = 3
sso_cli_max_attempts = 3
```

### **2. Session Duration Factors**

**SSO Session Duration is controlled by:**
- **AWS SSO Admin Settings**: 1-12 hours (configured in AWS SSO console)
- **Client Token Cache**: AWS CLI caches tokens locally
- **Role Session Duration**: Individual role temporary credentials (15min - 12 hours)

**Default AWS SSO Session Duration**: Usually 8 hours
**Role Session Duration**: Typically 1 hour for AdministratorAccess

## 🚀 **Session Management Scripts**

### **Quick SSO Login Script**
```powershell
# aws-sso-login.ps1
function Start-AWSSecuritySession {
    Write-Host "🔐 Starting AWS SSO session for Security Analytics Pipeline..." -ForegroundColor Cyan

    # Login to SSO
    aws sso login --profile security-analytics

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SSO login successful!" -ForegroundColor Green

        # Verify identity
        $identity = aws sts get-caller-identity --profile security-analytics | ConvertFrom-Json
        Write-Host "👤 Logged in as: $($identity.Arn)" -ForegroundColor Yellow
        Write-Host "🏢 Account: $($identity.Account)" -ForegroundColor Yellow

        # Set as default profile for session
        $env:AWS_PROFILE = "security-analytics"
        Write-Host "🎯 AWS_PROFILE set to: security-analytics" -ForegroundColor Green
    } else {
        Write-Host "❌ SSO login failed" -ForegroundColor Red
    }
}

# Call the function
Start-AWSSecuritySession
```

### **Session Status Check Script**
```powershell
# aws-session-check.ps1
function Test-AWSSession {
    Write-Host "🔍 Checking AWS session status..." -ForegroundColor Cyan

    try {
        $identity = aws sts get-caller-identity --profile security-analytics 2>$null | ConvertFrom-Json

        if ($identity) {
            Write-Host "✅ Active session found!" -ForegroundColor Green
            Write-Host "👤 User: $($identity.Arn.Split('/')[-1])" -ForegroundColor Yellow
            Write-Host "🏢 Account: $($identity.Account)" -ForegroundColor Yellow

            # Check token expiration (approximate)
            $cacheDir = "$env:USERPROFILE\.aws\sso\cache"
            if (Test-Path $cacheDir) {
                $latestCache = Get-ChildItem $cacheDir -Filter "*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
                if ($latestCache) {
                    $hoursOld = [math]::Round(((Get-Date) - $latestCache.LastWriteTime).TotalHours, 1)
                    Write-Host "⏰ Session cache age: $hoursOld hours" -ForegroundColor Cyan

                    if ($hoursOld -gt 7) {
                        Write-Host "⚠️  Session may expire soon - consider refreshing" -ForegroundColor Yellow
                    }
                }
            }

            return $true
        }
    } catch {
        Write-Host "❌ No valid session found" -ForegroundColor Red
        Write-Host "💡 Run: aws sso login --profile security-analytics" -ForegroundColor Yellow
        return $false
    }
}

# Call the function
Test-AWSSession
```

### **Automatic Session Refresh Script**
```powershell
# aws-auto-refresh.ps1
function Start-AWSAutoRefresh {
    param(
        [int]$CheckIntervalMinutes = 30,
        [int]$RefreshThresholdHours = 7
    )

    Write-Host "🔄 Starting AWS session auto-refresh monitor..." -ForegroundColor Cyan
    Write-Host "📊 Check interval: $CheckIntervalMinutes minutes" -ForegroundColor Yellow
    Write-Host "⏰ Refresh threshold: $RefreshThresholdHours hours" -ForegroundColor Yellow

    while ($true) {
        $sessionValid = Test-AWSSession

        if (-not $sessionValid) {
            Write-Host "🔐 Session expired - attempting refresh..." -ForegroundColor Yellow
            aws sso login --profile security-analytics
        }

        Start-Sleep -Seconds ($CheckIntervalMinutes * 60)
    }
}

# Uncomment to start auto-refresh
# Start-AWSAutoRefresh
```

## 💡 **Best Practices for Extended Sessions**

### **1. Set Default Profile Environment Variable**
```powershell
# Add to your PowerShell profile
$env:AWS_PROFILE = "security-analytics"
```

### **2. Create Aliases for Common Commands**
```powershell
# Add to PowerShell profile
function aws-login { aws sso login --profile security-analytics }
function aws-check { aws sts get-caller-identity --profile security-analytics }
function aws-refresh { aws sso login --profile security-analytics --force }
```

### **3. VS Code Integration**
Add to your VS Code settings:
```json
{
    "aws.profile": "security-analytics",
    "terminal.integrated.env.windows": {
        "AWS_PROFILE": "security-analytics"
    }
}
```

## 📋 **Project-Specific Session Management**

### **For Security Analytics Pipeline Development**
```powershell
# security-analytics-session.ps1
function Start-SecurityAnalyticsSession {
    # Login to AWS
    aws sso login --profile security-analytics

    # Set environment variables
    $env:AWS_PROFILE = "security-analytics"
    $env:AWS_DEFAULT_REGION = "us-east-1"

    # Verify Terraform access
    Write-Host "🏗️ Checking Terraform state access..." -ForegroundColor Cyan
    aws s3 ls s3://terraform-state-bucket-name 2>$null

    # Check Lambda functions
    Write-Host "⚡ Checking Lambda functions..." -ForegroundColor Cyan
    aws lambda list-functions --query 'Functions[?contains(FunctionName, `security-analytics`)].FunctionName' --output table

    # Check Kinesis streams
    Write-Host "🌊 Checking Kinesis streams..." -ForegroundColor Cyan
    aws kinesis list-streams --query 'StreamNames[?contains(@, `security-analytics`)]' --output table

    Write-Host "✅ Security Analytics Pipeline session ready!" -ForegroundColor Green
}
```

## ⚡ **Quick Setup Commands**

```powershell
# Create session management directory
new-item -itemtype directory -path "scripts\aws-session" -force

# Set default profile
$env:AWS_PROFILE = "security-analytics"

# Quick login
aws sso login --profile security-analytics

# Verify access
aws sts get-caller-identity
```

## 🎯 **Cost Optimization Note**

Extended sessions are perfect for development, but remember:
- **Development**: Keep sessions active for productivity
- **Production**: Use IAM roles and assume role chains
- **CI/CD**: Use OIDC providers or IAM users with limited permissions
- **Cost Impact**: SSO itself has no additional cost

This configuration will significantly reduce the frequency of having to re-authenticate while maintaining security best practices for your AWS Security Analytics Pipeline project!
