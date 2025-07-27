# AWS Session Status Checker for Security Analytics Pipeline
# Simple version without Unicode characters for better compatibility

param(
    [switch]$Detailed,
    [switch]$Quiet
)

function Write-StatusMessage {
    param([string]$Message, [string]$Color = "White")
    if (-not $Quiet) {
        Write-Host $Message -ForegroundColor $Color
    }
}

function Test-AWSSession {
    Write-StatusMessage "Checking AWS session status..." "Cyan"

    try {
        # Check current identity
        $identity = aws sts get-caller-identity --profile security-analytics 2>$null | ConvertFrom-Json

        if ($identity) {
            Write-StatusMessage "SUCCESS: Active AWS session found!" "Green"
            Write-StatusMessage "User: $($identity.Arn.Split('/')[-1])" "Yellow"
            Write-StatusMessage "Account: $($identity.Account)" "Yellow"
            Write-StatusMessage "Role: $($identity.Arn.Split('/')[-2])" "Yellow"

            # Check environment variable
            if ($env:AWS_PROFILE -eq "security-analytics") {
                Write-StatusMessage "AWS_PROFILE environment variable set correctly" "Green"
            }
            else {
                Write-StatusMessage "WARNING: AWS_PROFILE not set - run: `$env:AWS_PROFILE = 'security-analytics'" "Yellow"
            }

            # Check token cache age
            $cacheDir = "$env:USERPROFILE\.aws\sso\cache"
            if (Test-Path $cacheDir) {
                $cacheFiles = Get-ChildItem $cacheDir -Filter "*.json" | Sort-Object LastWriteTime -Descending
                if ($cacheFiles.Count -gt 0) {
                    $latestCache = $cacheFiles[0]
                    $hoursOld = [math]::Round(((Get-Date) - $latestCache.LastWriteTime).TotalHours, 1)
                    $minutesOld = [math]::Round(((Get-Date) - $latestCache.LastWriteTime).TotalMinutes, 0)

                    if ($hoursOld -lt 1) {
                        Write-StatusMessage "Session cache age: $minutesOld minutes (very fresh)" "Green"
                    }
                    elseif ($hoursOld -lt 6) {
                        Write-StatusMessage "Session cache age: $hoursOld hours (good)" "Green"
                    }
                    elseif ($hoursOld -lt 8) {
                        Write-StatusMessage "Session cache age: $hoursOld hours (consider refreshing soon)" "Yellow"
                    }
                    else {
                        Write-StatusMessage "Session cache age: $hoursOld hours (may expire soon)" "Red"
                        Write-StatusMessage "SUGGESTION: Consider running: .\aws-sso-login.ps1 -Force" "Yellow"
                    }
                }
            }

            if ($Detailed) {
                Write-StatusMessage "`nDetailed Session Information:" "Cyan"

                # Check AWS CLI version
                $awsVersion = aws --version 2>$null
                Write-StatusMessage "AWS CLI: $awsVersion" "Gray"

                # Test infrastructure access
                Write-StatusMessage "`nInfrastructure Access Check:" "Cyan"

                # Test S3 access
                try {
                    $buckets = aws s3 ls --profile security-analytics 2>$null
                    if ($buckets) {
                        $bucketCount = ($buckets -split "`n").Count - 1
                        Write-StatusMessage "S3 Access: SUCCESS ($bucketCount buckets visible)" "Green"
                    }
                    else {
                        Write-StatusMessage "S3 Access: No buckets or access denied" "Yellow"
                    }
                }
                catch {
                    Write-StatusMessage "S3 Access: FAILED" "Red"
                }

                # Test Lambda access
                try {
                    $allLambdas = aws lambda list-functions --query 'Functions[].FunctionName' --output text --profile security-analytics 2>$null
                    $securityLambdas = aws lambda list-functions --query 'Functions[?contains(FunctionName, `security-analytics`)].FunctionName' --output text --profile security-analytics 2>$null

                    if ($allLambdas) {
                        $lambdaCount = ($allLambdas -split "`t").Count
                        $securityCount = if ($securityLambdas) { ($securityLambdas -split "`t").Count } else { 0 }
                        Write-StatusMessage "Lambda Access: SUCCESS ($lambdaCount total, $securityCount security-analytics)" "Green"
                    }
                    else {
                        Write-StatusMessage "Lambda Access: No functions visible" "Yellow"
                    }
                }
                catch {
                    Write-StatusMessage "Lambda Access: FAILED" "Red"
                }

                # Test Kinesis access
                try {
                    $streams = aws kinesis list-streams --query 'StreamNames' --output text --profile security-analytics 2>$null
                    if ($streams) {
                        $streamCount = ($streams -split "`t").Count
                        Write-StatusMessage "Kinesis Access: SUCCESS ($streamCount streams)" "Green"
                    }
                    else {
                        Write-StatusMessage "Kinesis Access: No streams visible" "Yellow"
                    }
                }
                catch {
                    Write-StatusMessage "Kinesis Access: FAILED" "Red"
                }

                # Test CloudWatch access
                try {
                    $dashboards = aws cloudwatch list-dashboards --query 'DashboardEntries[].DashboardName' --output text --profile security-analytics 2>$null
                    if ($dashboards) {
                        $dashboardCount = ($dashboards -split "`t").Count
                        Write-StatusMessage "CloudWatch Access: SUCCESS ($dashboardCount dashboards)" "Green"
                    }
                    else {
                        Write-StatusMessage "CloudWatch Access: No dashboards visible" "Yellow"
                    }
                }
                catch {
                    Write-StatusMessage "CloudWatch Access: FAILED" "Red"
                }
            }

            return $true
        }
    }
    catch {
        Write-StatusMessage "ERROR: No valid AWS session found" "Red"
        Write-StatusMessage "SOLUTION: Run: .\aws-sso-login.ps1" "Yellow"
        Write-StatusMessage "OR: aws sso login --profile security-analytics" "Gray"
        return $false
    }

    return $false
}

# Main execution
$sessionValid = Test-AWSSession

if (-not $Quiet) {
    Write-Host ""
    if ($sessionValid) {
        Write-Host "SUCCESS: Ready for Security Analytics Pipeline development!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Quick Commands:" -ForegroundColor Cyan
        Write-Host "  cd terraform && terraform plan                     # Check infrastructure" -ForegroundColor Gray
        Write-Host "  cd testing && python test_pipeline.py             # Test pipeline" -ForegroundColor Gray
        Write-Host "  .\aws-session-check.ps1 -Detailed                 # Detailed status" -ForegroundColor Gray
    }
    else {
        Write-Host "Session Management:" -ForegroundColor Cyan
        Write-Host "  .\aws-sso-login.ps1                               # Login" -ForegroundColor Gray
        Write-Host "  .\aws-sso-login.ps1 -Force                        # Force refresh" -ForegroundColor Gray
    }
}

# Return success/failure for automation
exit $(if ($sessionValid) { 0 } else { 1 })
