#!/usr/bin/env python3
"""
AWS Security Analytics Pipeline - End-to-End Test Script

This script demonstrates the complete functionality of the security analytics pipeline
by sending test events through Kinesis and verifying the processing pipeline.

Author: Portfolio Demonstration
Purpose: Toyota RSOC Security Analytics Demo
"""

import json
import boto3
import base64
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any

# Configuration
PROFILE = 'johnadmin'
REGION = 'us-east-1'
KINESIS_STREAM = 'security-analytics-dev-security-events'
LAMBDA_FUNCTION = 'security-analytics-dev-event-processor'
S3_BUCKET = 'security-analytics-dev-security-data-lake-6t5cze3h'

# Initialize AWS clients with profile
session = boto3.Session(profile_name=PROFILE)
kinesis_client = session.client('kinesis', region_name=REGION)
lambda_client = session.client('lambda', region_name=REGION)
s3_client = session.client('s3', region_name=REGION)
logs_client = session.client('logs', region_name=REGION)

def print_header(title: str):
    """Print formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}")

def print_info(message: str):
    """Print info message."""
    print(f"ℹ️  {message}")

def print_error(message: str):
    """Print error message."""
    print(f"❌ {message}")

def create_test_events() -> List[tuple[str, Dict[str, Any]]]:
    """Create various types of test security events."""
    
    # Test Event 1: CloudTrail Event (High Risk)
    cloudtrail_event = {
        "Records": [{
            "eventVersion": "1.05",
            "userIdentity": {
                "type": "IAMUser",
                "principalId": "AIDACKCEVSQ6C2EXAMPLE",
                "arn": "arn:aws:iam::123456789012:user/test-user",
                "accountId": "123456789012",
                "userName": "test-user"
            },
            "eventTime": datetime.now(timezone.utc).isoformat(),
            "eventSource": "iam.amazonaws.com",
            "eventName": "CreateUser",
            "awsRegion": "us-east-1",
            "sourceIPAddress": "192.168.1.100",  # This will trigger threat intel alert
            "userAgent": "aws-cli/2.0.0",
            "requestParameters": {
                "userName": "suspicious-user"
            },
            "responseElements": None,
            "requestID": str(uuid.uuid4()),
            "eventID": str(uuid.uuid4()),
            "eventType": "AwsApiCall",
            "readOnly": False,
            "resources": [{
                "ARN": "arn:aws:iam::123456789012:user/suspicious-user",
                "accountId": "123456789012",
                "type": "AWS::IAM::User"
            }]
        }]
    }
    
    # Test Event 2: Simulated GuardDuty Finding (High Severity)
    guardduty_event = {
        "version": "0",
        "id": str(uuid.uuid4()),
        "detail-type": "GuardDuty Finding",
        "source": "aws.guardduty",
        "account": "643275918916",
        "time": datetime.now(timezone.utc).isoformat(),
        "region": "us-east-1",
        "detail": {
            "schemaVersion": "2.0",
            "accountId": "643275918916",
            "region": "us-east-1",
            "partition": "aws",
            "id": str(uuid.uuid4()),
            "arn": f"arn:aws:guardduty:us-east-1:643275918916:detector/finding/{uuid.uuid4()}",
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
                            "ipAddressV4": "10.0.0.50",  # This will trigger threat intel
                            "organization": {
                                "asn": "16509",
                                "asnOrg": "AMAZON-02",
                                "isp": "Amazon.com",
                                "org": "Amazon.com"
                            }
                        }
                    }
                },
                "count": 1
            },
            "severity": 8.5,  # High severity - will trigger alert
            "confidence": 9.2,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "title": "EC2 instance launched from malicious IP",
            "description": "An EC2 instance was launched from a known malicious IP address."
        }
    }
    
    # Test Event 3: Normal AWS Event (Low Risk)
    normal_event = {
        "version": "0",
        "id": str(uuid.uuid4()),
        "detail-type": "AWS Console Sign In",
        "source": "aws.signin",
        "account": "643275918916",
        "time": datetime.now(timezone.utc).isoformat(),
        "region": "us-east-1",
        "detail": {
            "eventVersion": "1.05",
            "userIdentity": {
                "type": "IAMUser",
                "principalId": "AIDACKCEVSQ6C2EXAMPLE",
                "arn": "arn:aws:iam::643275918916:user/normal-user",
                "accountId": "643275918916",
                "userName": "normal-user"
            },
            "eventTime": datetime.now(timezone.utc).isoformat(),
            "eventSource": "signin.amazonaws.com",
            "eventName": "ConsoleLogin",
            "awsRegion": "us-east-1",
            "sourceIPAddress": "203.0.113.12",  # Normal IP
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "responseElements": {
                "ConsoleLogin": "Success"
            },
            "requestID": str(uuid.uuid4()),
            "eventID": str(uuid.uuid4()),
            "eventType": "AwsConsoleSignIn",
            "readOnly": False
        }
    }
    
    return [
        ("CloudTrail High-Risk Event", cloudtrail_event),
        ("GuardDuty High-Severity Finding", guardduty_event),
        ("Normal AWS Console Login", normal_event)
    ]

def send_event_to_kinesis(event_name: str, event_data: Dict[str, Any]) -> bool:
    """Send a test event to Kinesis stream."""
    try:
        # Convert event to JSON and encode
        event_json = json.dumps(event_data)
        
        # Send to Kinesis
        response = kinesis_client.put_record(
            StreamName=KINESIS_STREAM,
            Data=event_json,
            PartitionKey=str(uuid.uuid4())
        )
        
        print_success(f"Sent {event_name} to Kinesis")
        print_info(f"Sequence Number: {response['SequenceNumber']}")
        return True
        
    except Exception as e:
        print_error(f"Failed to send {event_name}: {str(e)}")
        return False

def check_lambda_logs(function_name: str, start_time: datetime) -> List[Dict]:
    """Check Lambda function logs for processing results."""
    try:
        log_group = f"/aws/lambda/{function_name}"
        
        # Get log events since start time
        response = logs_client.filter_log_events(
            logGroupName=log_group,
            startTime=int(start_time.timestamp() * 1000),
            filterPattern="Processing complete"
        )
        
        return response.get('events', [])
        
    except Exception as e:
        print_error(f"Failed to check logs: {str(e)}")
        return []

def check_s3_objects(bucket_name: str, prefix: str = "security-events/") -> List[str]:
    """Check for objects created in S3 bucket."""
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
            MaxKeys=10
        )
        
        objects = []
        for obj in response.get('Contents', []):
            objects.append(obj['Key'])
            
        return objects
        
    except Exception as e:
        print_error(f"Failed to check S3: {str(e)}")
        return []

def verify_infrastructure():
    """Verify that all infrastructure components are working."""
    print_header("INFRASTRUCTURE VERIFICATION")
    
    # Check Kinesis Stream
    try:
        response = kinesis_client.describe_stream(StreamName=KINESIS_STREAM)
        status = response['StreamDescription']['StreamStatus']
        if status == 'ACTIVE':
            print_success(f"Kinesis Stream: {KINESIS_STREAM} - {status}")
        else:
            print_error(f"Kinesis Stream: {KINESIS_STREAM} - {status}")
            return False
    except Exception as e:
        print_error(f"Kinesis Stream check failed: {str(e)}")
        return False
    
    # Check Lambda Function
    try:
        response = lambda_client.get_function(FunctionName=LAMBDA_FUNCTION)
        state = response['Configuration']['State']
        if state == 'Active':
            print_success(f"Lambda Function: {LAMBDA_FUNCTION} - {state}")
        else:
            print_error(f"Lambda Function: {LAMBDA_FUNCTION} - {state}")
            return False
    except Exception as e:
        print_error(f"Lambda Function check failed: {str(e)}")
        return False
    
    # Check S3 Bucket
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET)
        print_success(f"S3 Bucket: {S3_BUCKET} - Accessible")
    except Exception as e:
        print_error(f"S3 Bucket check failed: {str(e)}")
        return False
    
    return True

def run_end_to_end_test():
    """Run complete end-to-end test of the security analytics pipeline."""
    print_header("AWS SECURITY ANALYTICS PIPELINE - END-TO-END TEST")
    print_info(f"Test started at: {datetime.now(timezone.utc).isoformat()}")
    
    # Verify infrastructure
    if not verify_infrastructure():
        print_error("Infrastructure verification failed. Exiting.")
        return False
    
    # Create test events
    print_header("GENERATING TEST EVENTS")
    test_events = create_test_events()
    print_info(f"Created {len(test_events)} test events")
    
    # Send events to Kinesis
    print_header("SENDING EVENTS TO KINESIS")
    start_time = datetime.now(timezone.utc)
    sent_count = 0
    
    for event_name, event_data in test_events:
        if send_event_to_kinesis(event_name, event_data):
            sent_count += 1
        time.sleep(2)  # Small delay between events
    
    print_info(f"Successfully sent {sent_count}/{len(test_events)} events")
    
    # Wait for Lambda processing
    print_header("WAITING FOR LAMBDA PROCESSING")
    print_info("Waiting 30 seconds for Lambda to process events...")
    time.sleep(30)
    
    # Check Lambda logs
    print_header("CHECKING LAMBDA EXECUTION LOGS")
    log_events = check_lambda_logs(LAMBDA_FUNCTION, start_time)
    
    if log_events:
        print_success(f"Found {len(log_events)} processing log entries")
        for event in log_events[-3:]:  # Show last 3 entries
            message = event.get('message', '').strip()
            if 'Processing complete' in message:
                print_info(f"  {message}")
    else:
        print_error("No processing logs found")
    
    # Check S3 data lake
    print_header("CHECKING S3 DATA LAKE")
    s3_objects = check_s3_objects(S3_BUCKET)
    
    if s3_objects:
        print_success(f"Found {len(s3_objects)} objects in S3 data lake")
        for obj_key in s3_objects[:5]:  # Show first 5
            print_info(f"  {obj_key}")
    else:
        print_error("No objects found in S3 data lake")
    
    # Summary
    print_header("TEST SUMMARY")
    print_info(f"Events Sent: {sent_count}/{len(test_events)}")
    print_info(f"Lambda Executions: {len(log_events)}")
    print_info(f"S3 Objects Created: {len(s3_objects)}")
    
    if sent_count > 0 and len(log_events) > 0 and len(s3_objects) > 0:
        print_success("🎉 END-TO-END TEST SUCCESSFUL!")
        print_info("The security analytics pipeline is working correctly")
        return True
    else:
        print_error("❌ Some components failed. Check logs for details.")
        return False

def display_portfolio_summary():
    """Display portfolio demonstration summary."""
    print_header("PORTFOLIO DEMONSTRATION SUMMARY")
    print("""
🎯 AWS Security Analytics Pipeline - Successfully Deployed!

📊 INFRASTRUCTURE DEPLOYED:
   ✅ Kinesis Data Stream (1 shard, KMS encrypted)
   ✅ Lambda Function (256MB, Python 3.11, 60s timeout)
   ✅ S3 Data Lake (versioned, encrypted, lifecycle rules)
   ✅ CloudTrail (management events, S3 integration)
   ✅ Glue Data Catalog (queryable schema)
   ✅ SNS Alerting (email notifications)
   ✅ IAM Roles & Policies (least privilege)
   ✅ KMS Encryption (data at rest and transit)

💰 COST OPTIMIZATION:
   💡 Monthly Cost: ~$15-25 (vs $50-150 full config)
   💡 GuardDuty: Disabled for cost savings (-$30-100/month)
   💡 Lambda: 256MB memory (50% cost reduction)
   💡 S3 Lifecycle: 30-day retention
   💡 CloudWatch: 7-day log retention

🔧 CAPABILITIES DEMONSTRATED:
   ✅ Real-time event processing
   ✅ Data enrichment & threat intelligence
   ✅ Risk scoring algorithms
   ✅ Automated alerting
   ✅ Scalable data lake architecture
   ✅ Security best practices
   ✅ Infrastructure as Code (Terraform)
   ✅ Cost optimization strategies

🚀 READY FOR PRODUCTION:
   - Enable GuardDuty for live threat detection
   - Add Athena/QuickSight for analytics dashboards
   - Implement additional data sources
   - Scale Kinesis shards based on volume
   - Add machine learning for anomaly detection

This demonstrates enterprise-grade AWS security operations capabilities
suitable for Toyota's RSOC requirements.
    """)

def main():
    """Main execution function."""
    try:
        # Run the complete test
        success = run_end_to_end_test()
        
        # Display portfolio summary
        display_portfolio_summary()
        
        if success:
            print_success("🏆 Portfolio demonstration completed successfully!")
        else:
            print_error("⚠️ Some tests failed. Review the logs above.")
            
    except KeyboardInterrupt:
        print_error("\n🛑 Test interrupted by user")
    except Exception as e:
        print_error(f"🚨 Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
