#!/usr/bin/env python3
"""
Enhanced Pipeline Test Script for Dashboard Demonstration

This script generates various security events to populate CloudWatch dashboards
and demonstrate the security analytics pipeline's capabilities.
"""

import json
import boto3
import time
import random
from datetime import datetime, timezone
from typing import Dict, List, Any

# Configure AWS
kinesis_client = boto3.client('kinesis', region_name='us-east-1')
sns_client = boto3.client('sns', region_name='us-east-1')

# Pipeline configuration
KINESIS_STREAM_NAME = "security-analytics-dev-security-events"
EVENTS_TO_GENERATE = 25  # More events for better dashboard visualization

def generate_cloudtrail_event(event_index: int) -> Dict[str, Any]:
    """Generate a realistic CloudTrail event"""
    base_time = datetime.now(timezone.utc)
    
    # Vary event types for diversity
    event_types = [
        "AssumeRole", "CreateUser", "DeleteUser", "AttachUserPolicy",
        "CreateBucket", "DeleteBucket", "GetObject", "PutObject",
        "RunInstances", "TerminateInstances", "StopInstances", "StartInstances",
        "CreateRole", "DeleteRole", "ModifyDBInstance", "CreateTable"
    ]
    
    # Simulate different source IPs (some suspicious)
    source_ips = [
        "192.168.1.100",  # Known bad IP from our threat intel
        "203.0.113.45",   # Random legitimate IP
        "198.51.100.67",  # Another legitimate IP
        "10.0.0.50",      # Another bad IP
        "172.16.0.25",    # Internal IP
        "52.95.110.1"     # AWS IP range
    ]
    
    # Vary user agents
    user_agents = [
        "aws-cli/2.11.22",
        "Boto3/1.26.137",
        "aws-sdk-python/1.26.137",
        "terraform/1.5.0",
        "[S3Console/0.4, aws-internal/3]"
    ]
    
    # Add some failed events for risk scoring
    success_rate = 0.85  # 85% success rate
    is_successful = random.random() < success_rate
    
    event = {
        "Records": [{
            "eventVersion": "1.08",
            "userIdentity": {
                "type": "IAMUser" if event_index % 3 == 0 else "AssumedRole",
                "principalId": f"AIDA{random.randint(100000000000000000, 999999999999999999)}",
                "arn": f"arn:aws:iam::643275918916:user/test-user-{event_index % 5}",
                "accountId": "643275918916",
                "userName": f"test-user-{event_index % 5}"
            },
            "eventTime": base_time.isoformat(),
            "eventSource": random.choice(["iam.amazonaws.com", "s3.amazonaws.com", "ec2.amazonaws.com"]),
            "eventName": random.choice(event_types),
            "awsRegion": "us-east-1",
            "sourceIPAddress": random.choice(source_ips),
            "userAgent": random.choice(user_agents),
            "requestParameters": {},
            "responseElements": {} if is_successful else None,
            "requestID": f"req-{random.randint(100000, 999999)}-{event_index}",
            "eventID": f"evt-{random.randint(100000000, 999999999)}-{event_index}",
            "readOnly": random.choice([True, False]),
            "eventType": "AwsApiCall",
            "managementEvent": True,
            "recipientAccountId": "643275918916"
        }]
    }
    
    # Add error details for failed events
    if not is_successful:
        event["Records"][0]["errorCode"] = random.choice([
            "AccessDenied", "InvalidUserID.NotFound", "UnauthorizedOperation"
        ])
        event["Records"][0]["errorMessage"] = "User is not authorized to perform this operation"
    
    return event

def generate_guardduty_event(event_index: int) -> Dict[str, Any]:
    """Generate a realistic GuardDuty finding event"""
    base_time = datetime.now(timezone.utc)
    
    # Various GuardDuty finding types
    finding_types = [
        "UnauthorizedAPICall:EC2/TorIPCaller",
        "CryptoCurrency:EC2/BitcoinTool.B!DNS",
        "Backdoor:EC2/C&CActivity.B!DNS",
        "Stealth:IAMUser/CloudTrailLoggingDisabled",
        "InstanceCredentialExfiltration:IAMUser/AnomalousBehavior",
        "Impact:EC2/WinRMBruteForce",
        "Persistence:IAMUser/NetworkPermissions",
        "Discovery:S3/BucketEnumeration.Unusual"
    ]
    
    # Vary severity levels
    severities = [1.0, 2.1, 4.5, 6.8, 7.2, 8.5, 9.1]
    severity = random.choice(severities)
    
    # High-risk IPs for some events
    high_risk_ips = ["185.220.101.45", "103.253.27.108", "94.102.49.190"]
    normal_ips = ["203.0.113.45", "198.51.100.67", "52.95.110.1"]
    
    source_ip = random.choice(high_risk_ips if severity > 6.0 else normal_ips)
    
    event = {
        "version": "0",
        "id": f"guardduty-event-{event_index}",
        "detail-type": "GuardDuty Finding",
        "source": "aws.guardduty",
        "account": "643275918916",
        "time": base_time.isoformat(),
        "region": "us-east-1",
        "detail": {
            "schemaVersion": "2.0",
            "accountId": "643275918916",
            "region": "us-east-1",
            "partition": "aws",
            "id": f"finding-{random.randint(100000000000000000, 999999999999999999)}",
            "arn": f"arn:aws:guardduty:us-east-1:643275918916:detector/detector-id/finding/finding-{event_index}",
            "type": random.choice(finding_types),
            "resource": {
                "resourceType": random.choice(["Instance", "S3Bucket", "IAMUser"]),
                "instanceDetails": {
                    "instanceId": f"i-{random.randint(100000000000000000, 999999999999999999):016x}"[:17],
                    "instanceType": "t3.micro",
                    "launchTime": base_time.isoformat(),
                    "platform": "Linux"
                } if random.choice([True, False]) else None
            },
            "service": {
                "serviceName": "guardduty",
                "detectorId": f"detector-{random.randint(100000000000000000, 999999999999999999):016x}"[:32],
                "action": {
                    "actionType": random.choice(["NETWORK_CONNECTION", "AWS_API_CALL", "DNS_REQUEST"]),
                    "networkConnectionAction": {
                        "connectionDirection": "OUTBOUND",
                        "remoteIpDetails": {
                            "ipAddressV4": source_ip,
                            "country": {
                                "countryName": random.choice(["United States", "Russia", "China", "Netherlands"])
                            },
                            "city": {
                                "cityName": random.choice(["Seattle", "Moscow", "Beijing", "Amsterdam"])
                            },
                            "geoLocation": {
                                "lat": random.uniform(-90, 90),
                                "lon": random.uniform(-180, 180)
                            }
                        },
                        "protocol": "TCP",
                        "localPortDetails": {
                            "port": random.randint(32768, 65535),
                            "portName": "Unknown"
                        },
                        "remotePortDetails": {
                            "port": random.choice([80, 443, 22, 3389, 8080]),
                            "portName": random.choice(["HTTP", "HTTPS", "SSH", "RDP", "HTTP-ALT"])
                        }
                    } if random.choice([True, False]) else None
                },
                "count": random.randint(1, 10),
                "eventFirstSeen": base_time.isoformat(),
                "eventLastSeen": base_time.isoformat(),
                "archived": False
            },
            "severity": severity,
            "confidence": random.uniform(7.0, 10.0),
            "createdAt": base_time.isoformat(),
            "updatedAt": base_time.isoformat(),
            "title": f"Sample finding {event_index}",
            "description": f"This is a test GuardDuty finding for demonstration purposes (Event {event_index})"
        }
    }
    
    return event

def generate_custom_security_event(event_index: int) -> Dict[str, Any]:
    """Generate a custom security event"""
    base_time = datetime.now(timezone.utc)
    
    event_types = [
        "login_anomaly", "privilege_escalation", "data_exfiltration_attempt",
        "suspicious_network_activity", "unauthorized_access_attempt"
    ]
    
    risk_scores = [15, 25, 45, 65, 75, 85, 95]
    
    return {
        "source": "custom.security",
        "detail-type": "Security Event",
        "detail": {
            "event_type": random.choice(event_types),
            "severity": random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
            "risk_score": random.choice(risk_scores),
            "user_id": f"user-{event_index % 10}",
            "source_ip": random.choice([
                "192.168.1.100", "10.0.0.50", "203.0.113.45", "198.51.100.67"
            ]),
            "timestamp": base_time.isoformat(),
            "additional_context": {
                "user_agent": "Custom Security Agent v1.0",
                "detection_method": "behavioral_analysis",
                "confidence": random.uniform(0.7, 1.0)
            }
        },
        "account": "643275918916",
        "region": "us-east-1",
        "time": base_time.isoformat()
    }

def send_events_in_batches():
    """Send events in batches to create realistic dashboard activity"""
    print(f"🚀 Starting enhanced pipeline test with {EVENTS_TO_GENERATE} events...")
    print("📊 This will populate the CloudWatch dashboards with realistic data\n")
    
    successful_events = 0
    failed_events = 0
    
    # Send events in waves with different delays
    for wave in range(5):  # 5 waves of events
        print(f"📈 Wave {wave + 1}/5 - Sending events...")
        
        wave_events = EVENTS_TO_GENERATE // 5
        for i in range(wave_events):
            event_index = wave * wave_events + i
            
            try:
                # Vary event types for diversity
                if event_index % 3 == 0:
                    event = generate_cloudtrail_event(event_index)
                    event_type = "CloudTrail"
                elif event_index % 3 == 1:
                    event = generate_guardduty_event(event_index)
                    event_type = "GuardDuty"
                else:
                    event = generate_custom_security_event(event_index)
                    event_type = "Custom"
                
                # Send to Kinesis
                response = kinesis_client.put_record(
                    StreamName=KINESIS_STREAM_NAME,
                    Data=json.dumps(event),
                    PartitionKey=f"partition-{event_index % 10}"  # Distribute across partitions
                )
                
                print(f"✅ Event {event_index + 1} ({event_type}) sent - Sequence: {response['SequenceNumber'][:10]}...")
                successful_events += 1
                
                # Small delay between events to spread them over time
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Failed to send event {event_index + 1}: {str(e)}")
                failed_events += 1
        
        # Longer pause between waves to create distinct activity periods
        if wave < 4:  # Don't wait after the last wave
            print(f"⏱️  Waiting 10 seconds before next wave...\n")
            time.sleep(10)
    
    return successful_events, failed_events

def verify_dashboard_data():
    """Check that data is flowing for dashboard visibility"""
    print("\n🔍 Verifying pipeline data flow...")
    
    try:
        # Check Kinesis stream metrics
        cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
        
        # Get recent Kinesis metrics
        end_time = datetime.now(timezone.utc)
        start_time = datetime.fromtimestamp(end_time.timestamp() - 300, timezone.utc)  # Last 5 minutes
        
        metrics = cloudwatch.get_metric_statistics(
            Namespace='AWS/Kinesis',
            MetricName='IncomingRecords',
            Dimensions=[
                {
                    'Name': 'StreamName',
                    'Value': KINESIS_STREAM_NAME
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=['Sum']
        )
        
        total_records = sum(point['Sum'] for point in metrics['Datapoints'])
        print(f"📊 Kinesis stream processed {total_records} records in the last 5 minutes")
        
        # Check Lambda metrics
        lambda_metrics = cloudwatch.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='Invocations',
            Dimensions=[
                {
                    'Name': 'FunctionName',
                    'Value': 'security-analytics-dev-event-processor'
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=['Sum']
        )
        
        total_invocations = sum(point['Sum'] for point in lambda_metrics['Datapoints'])
        print(f"⚡ Lambda function invoked {total_invocations} times in the last 5 minutes")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Could not verify metrics: {str(e)}")
        return False

def main():
    """Main execution function"""
    start_time = time.time()
    
    print("🎯 AWS Security Analytics Pipeline - Enhanced Dashboard Test")
    print("=" * 60)
    print("This script will:")
    print("1. Generate diverse security events (CloudTrail, GuardDuty, Custom)")
    print("2. Send events in waves to create realistic activity patterns")
    print("3. Populate CloudWatch dashboards with data")
    print("4. Verify data flow through the pipeline")
    print("=" * 60)
    
    # Send events
    successful, failed = send_events_in_batches()
    
    # Wait for processing
    print("\n⏳ Waiting 30 seconds for event processing...")
    time.sleep(30)
    
    # Verify pipeline
    verify_dashboard_data()
    
    # Summary
    execution_time = time.time() - start_time
    print(f"\n📋 Test Summary:")
    print(f"   ✅ Successful events: {successful}")
    print(f"   ❌ Failed events: {failed}")
    print(f"   ⏱️  Execution time: {execution_time:.1f} seconds")
    print(f"   📊 Dashboard data should now be visible!")
    
    # Dashboard URLs
    print(f"\n🎨 View your dashboards:")
    print(f"   📈 Security Analytics: https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=security-analytics-security-analytics-dashboard")
    print(f"   🔢 Security Metrics: https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=security-analytics-security-metrics-dashboard")
    print(f"   💰 Cost Tracking: https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=security-analytics-cost-tracking-dashboard")

if __name__ == "__main__":
    main()
