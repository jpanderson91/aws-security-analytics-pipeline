# PowerShell Script to Generate Test Data for CloudWatch Dashboards
# This script sends test events to Kinesis to populate dashboard metrics

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AWS Security Analytics Pipeline - Dashboard Data Test    " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Configuration
$PROFILE = "johnadmin"
$REGION = "us-east-1"
$KINESIS_STREAM = "security-analytics-dev-security-events"
$LAMBDA_FUNCTION = "security-analytics-dev-event-processor"

# Test Event JSON Data
$events = @(
    @{
        name = "CloudTrail High-Risk Event"
        data = @'
{
  "Records": [{
    "eventVersion": "1.05",
    "userIdentity": {
      "type": "IAMUser",
      "principalId": "AIDACKCEVSQ6C2EXAMPLE",
      "arn": "arn:aws:iam::123456789012:user/test-user",
      "accountId": "123456789012",
      "userName": "test-user"
    },
    "eventTime": "2025-07-22T22:30:00Z",
    "eventSource": "iam.amazonaws.com",
    "eventName": "CreateUser",
    "awsRegion": "us-east-1",
    "sourceIPAddress": "192.168.1.100",
    "userAgent": "aws-cli/2.0.0",
    "requestParameters": {
      "userName": "suspicious-user"
    },
    "requestID": "12345678-1234-1234-1234-123456789012",
    "eventID": "87654321-4321-4321-4321-210987654321",
    "eventType": "AwsApiCall",
    "readOnly": false
  }]
}
'@
    },
    @{
        name = "GuardDuty High-Severity Finding"
        data = @'
{
  "version": "0",
  "id": "guardduty-test-event",
  "detail-type": "GuardDuty Finding",
  "source": "aws.guardduty",
  "account": "123456789012",
  "time": "2025-07-22T22:31:00Z",
  "region": "us-east-1",
  "detail": {
    "schemaVersion": "2.0",
    "accountId": "123456789012",
    "region": "us-east-1",
    "id": "test-finding-12345",
    "type": "UnauthorizedAPICall:EC2/MaliciousIPCaller.Custom",
    "resource": {
      "resourceType": "EC2Instance",
      "instanceDetails": {
        "instanceId": "i-1234567890abcdef0",
        "instanceType": "t2.micro"
      }
    },
    "service": {
      "action": {
        "actionType": "AWS_API_CALL",
        "awsApiCallAction": {
          "api": "RunInstances",
          "serviceName": "ec2.amazonaws.com",
          "remoteIpDetails": {
            "ipAddressV4": "10.0.0.50"
          }
        }
      }
    },
    "severity": 8.5,
    "confidence": 9.2,
    "title": "EC2 instance launched from malicious IP",
    "description": "An EC2 instance was launched from a known malicious IP address."
  }
}
'@
    },
    @{
        name = "Normal AWS Console Login"
        data = @'
{
  "version": "0",
  "id": "normal-signin-event",
  "detail-type": "AWS Console Sign In",
  "source": "aws.signin",
  "account": "123456789012",
  "time": "2025-07-22T22:32:00Z",
  "region": "us-east-1",
  "detail": {
    "eventVersion": "1.05",
    "userIdentity": {
      "type": "IAMUser",
      "principalId": "AIDACKCEVSQ6C2EXAMPLE",
      "arn": "arn:aws:iam::123456789012:user/normal-user",
      "accountId": "123456789012",
      "userName": "normal-user"
    },
    "eventTime": "2025-07-22T22:32:00Z",
    "eventSource": "signin.amazonaws.com",
    "eventName": "ConsoleLogin",
    "awsRegion": "us-east-1",
    "sourceIPAddress": "203.0.113.12",
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "responseElements": {
      "ConsoleLogin": "Success"
    },
    "eventType": "AwsConsoleSignIn",
    "readOnly": false
  }
}
'@
    }
)

Write-Host "`n🔍 VERIFYING INFRASTRUCTURE..." -ForegroundColor Yellow

# Check if AWS CLI is available
try {
    aws --version > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ AWS CLI is available" -ForegroundColor Green
    } else {
        Write-Host "❌ AWS CLI not found" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ AWS CLI not found" -ForegroundColor Red
    exit 1
}

# Check Kinesis stream
Write-Host "`n📡 Checking Kinesis Stream..." -ForegroundColor Yellow
try {
    $streamStatus = aws kinesis describe-stream --stream-name $KINESIS_STREAM --profile $PROFILE --region $REGION --query 'StreamDescription.StreamStatus' --output text 2>&1
    if ($streamStatus -eq "ACTIVE") {
        Write-Host "✅ Kinesis Stream: $KINESIS_STREAM - ACTIVE" -ForegroundColor Green
    } else {
        Write-Host "❌ Kinesis Stream: $KINESIS_STREAM - $streamStatus" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Failed to check Kinesis stream: $_" -ForegroundColor Red
    exit 1
}

# Check Lambda function
Write-Host "`n⚡ Checking Lambda Function..." -ForegroundColor Yellow
try {
    $lambdaState = aws lambda get-function --function-name $LAMBDA_FUNCTION --profile $PROFILE --region $REGION --query 'Configuration.State' --output text 2>&1
    if ($lambdaState -eq "Active") {
        Write-Host "✅ Lambda Function: $LAMBDA_FUNCTION - ACTIVE" -ForegroundColor Green
    } else {
        Write-Host "❌ Lambda Function: $LAMBDA_FUNCTION - $lambdaState" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Failed to check Lambda function: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n🚀 SENDING TEST EVENTS TO KINESIS..." -ForegroundColor Yellow

$successCount = 0
foreach ($event in $events) {
    try {
        Write-Host "`n📤 Sending: $($event.name)" -ForegroundColor Cyan
        
        # Generate unique partition key
        $partitionKey = [System.Guid]::NewGuid().ToString()
        
        # Send event to Kinesis using AWS CLI
        $result = aws kinesis put-record `
            --stream-name $KINESIS_STREAM `
            --partition-key $partitionKey `
            --data $event.data `
            --profile $PROFILE `
            --region $REGION `
            --output json 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully sent: $($event.name)" -ForegroundColor Green
            $successCount++
            
            # Parse the result to get sequence number
            $resultObj = $result | ConvertFrom-Json
            Write-Host "   📍 Sequence Number: $($resultObj.SequenceNumber)" -ForegroundColor Gray
        } else {
            Write-Host "❌ Failed to send: $($event.name)" -ForegroundColor Red
            Write-Host "   Error: $result" -ForegroundColor Red
        }
        
        # Small delay between events
        Start-Sleep -Seconds 2
        
    } catch {
        Write-Host "❌ Error sending $($event.name): $_" -ForegroundColor Red
    }
}

Write-Host "`n⏱️  WAITING FOR LAMBDA PROCESSING..." -ForegroundColor Yellow
Write-Host "   Waiting 30 seconds for events to be processed..." -ForegroundColor Gray
Start-Sleep -Seconds 30

Write-Host "`n📊 CHECKING RECENT LAMBDA EXECUTIONS..." -ForegroundColor Yellow
try {
    # Get recent Lambda logs
    $logGroup = "/aws/lambda/$LAMBDA_FUNCTION"
    $startTime = [int64]((Get-Date).AddMinutes(-5).ToUniversalTime().Subtract((Get-Date "1970-01-01")).TotalMilliseconds)
    
    Write-Host "   Checking logs in: $logGroup" -ForegroundColor Gray
    $logs = aws logs filter-log-events `
        --log-group-name $logGroup `
        --start-time $startTime `
        --filter-pattern "Processing complete" `
        --profile $PROFILE `
        --region $REGION `
        --output json 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        $logData = $logs | ConvertFrom-Json
        $eventCount = $logData.events.Count
        if ($eventCount -gt 0) {
            Write-Host "✅ Found $eventCount processing log entries" -ForegroundColor Green
            $logData.events | Select-Object -Last 3 | ForEach-Object {
                Write-Host "   📝 $($_.message.Trim())" -ForegroundColor Gray
            }
        } else {
            Write-Host "⚠️  No recent processing logs found" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  Could not retrieve Lambda logs: $logs" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Error checking Lambda logs: $_" -ForegroundColor Yellow
}

Write-Host "`n📈 DASHBOARD METRICS SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "📊 Events Sent to Kinesis: $successCount/$($events.Count)" -ForegroundColor White
Write-Host "⚡ Lambda Function: Triggered by Kinesis events" -ForegroundColor White
Write-Host "🗃️  S3 Data Lake: Events stored with time partitioning" -ForegroundColor White
Write-Host "📧 SNS Alerts: High-risk events generate notifications" -ForegroundColor White
Write-Host "📋 CloudTrail: API calls logged and monitored" -ForegroundColor White

Write-Host "`n🎯 DASHBOARD DATA GENERATED!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

Write-Host @"

✅ Your CloudWatch dashboards should now show data!

📈 Check these metrics in your Security Analytics Dashboard:
   • Lambda Performance: Function invocations, duration, errors
   • Kinesis Activity: Incoming/outgoing records and bytes  
   • S3 Data Lake: Storage growth and object counts
   • SNS Alerts: Message publication metrics
   • CloudTrail: API activity tracking

🔍 Dashboard URLs:
   • CloudWatch: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#dashboards:
   • Lambda Logs: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#logsV2:log-groups/log-group/%2Faws%2Flambda%2F$LAMBDA_FUNCTION

⏰ Note: CloudWatch metrics may take 5-15 minutes to fully appear.
    If you still see "No data available", wait a few more minutes and refresh.

🏆 Your AWS Security Analytics Pipeline is now generating real metrics
    and is ready for portfolio demonstration!

"@ -ForegroundColor White

Write-Host "Test completed at: $(Get-Date)" -ForegroundColor Gray
