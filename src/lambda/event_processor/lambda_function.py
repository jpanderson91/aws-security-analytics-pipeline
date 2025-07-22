"""
AWS Security Analytics Pipeline - Event Processor Lambda Function

This Lambda function processes security events from Kinesis streams,
enriches the data, and stores it in S3 for further analysis.

Author: Portfolio Demonstration
Purpose: Toyota RSOC Security Analytics
"""

import json
import boto3
import base64
import gzip
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import uuid

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

# Initialize AWS clients
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

# Environment variables
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for processing security events from Kinesis.
    
    Args:
        event: Kinesis event containing security data
        context: Lambda context object
        
    Returns:
        Processing results and statistics
    """
    logger.info(f"Processing {len(event['Records'])} records")
    
    processed_records = 0
    failed_records = 0
    alerts_generated = 0
    
    try:
        for record in event['Records']:
            try:
                # Decode Kinesis record
                kinesis_data = record['kinesis']
                payload = base64.b64decode(kinesis_data['data'])
                
                # Handle compressed data
                if payload.startswith(b'\x1f\x8b'):  # gzip magic number
                    payload = gzip.decompress(payload)
                
                # Parse JSON data
                event_data = json.loads(payload.decode('utf-8'))
                
                # Process the security event
                processed_event = process_security_event(event_data)
                
                # Store in S3
                store_event_in_s3(processed_event)
                
                # Check for high-severity alerts
                if should_generate_alert(processed_event):
                    generate_security_alert(processed_event)
                    alerts_generated += 1
                
                processed_records += 1
                
            except Exception as e:
                logger.error(f"Failed to process record: {str(e)}")
                failed_records += 1
                continue
    
    except Exception as e:
        logger.error(f"Critical error in lambda_handler: {str(e)}")
        raise
    
    # Log processing statistics
    logger.info(f"Processing complete: {processed_records} successful, {failed_records} failed, {alerts_generated} alerts")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'processed_records': processed_records,
            'failed_records': failed_records,
            'alerts_generated': alerts_generated,
            'execution_time': context.get_remaining_time_in_millis() if context else 0
        })
    }


def process_security_event(raw_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process and enrich a security event.
    
    Args:
        raw_event: Raw security event data
        
    Returns:
        Enriched security event
    """
    processed_event = {
        'event_id': str(uuid.uuid4()),
        'processed_at': datetime.now(timezone.utc).isoformat(),
        'raw_event': raw_event
    }
    
    # Extract common fields based on event source
    if 'source' in raw_event:
        processed_event.update(extract_aws_event_fields(raw_event))
    elif 'detail' in raw_event and 'type' in raw_event['detail']:
        processed_event.update(extract_guardduty_fields(raw_event))
    elif 'Records' in raw_event:
        processed_event.update(extract_cloudtrail_fields(raw_event))
    
    # Add risk scoring
    processed_event['risk_score'] = calculate_risk_score(processed_event)
    
    # Add geographic enrichment
    if 'source_ip' in processed_event:
        processed_event['geo_info'] = enrich_ip_geolocation(processed_event['source_ip'])
    
    # Add threat intelligence
    processed_event['threat_intel'] = check_threat_intelligence(processed_event)
    
    return processed_event


def extract_aws_event_fields(event: Dict[str, Any]) -> Dict[str, Any]:
    """Extract fields from general AWS events."""
    return {
        'event_type': 'aws_event',
        'source': event.get('source', 'unknown'),
        'detail_type': event.get('detail-type', 'unknown'),
        'account': event.get('account', 'unknown'),
        'region': event.get('region', 'unknown'),
        'event_time': event.get('time', datetime.now(timezone.utc).isoformat()),
        'resources': event.get('resources', [])
    }


def extract_guardduty_fields(event: Dict[str, Any]) -> Dict[str, Any]:
    """Extract fields from GuardDuty findings."""
    detail = event.get('detail', {})
    service = detail.get('service', {})
    
    return {
        'event_type': 'guardduty_finding',
        'finding_id': detail.get('id', 'unknown'),
        'finding_type': detail.get('type', 'unknown'),
        'severity': detail.get('severity', 0),
        'confidence': detail.get('confidence', 0),
        'account': detail.get('accountId', 'unknown'),
        'region': detail.get('region', 'unknown'),
        'event_time': detail.get('createdAt', datetime.now(timezone.utc).isoformat()),
        'resource_type': detail.get('resource', {}).get('resourceType', 'unknown'),
        'source_ip': extract_source_ip_from_guardduty(detail),
        'user_identity': extract_user_identity_from_guardduty(detail),
        'action': service.get('action', {}),
        'count': service.get('count', 1)
    }


def extract_cloudtrail_fields(event: Dict[str, Any]) -> Dict[str, Any]:
    """Extract fields from CloudTrail events."""
    records = event.get('Records', [])
    if not records:
        return {}
    
    # Process first record (expand for multiple records if needed)
    record = records[0]
    
    return {
        'event_type': 'cloudtrail_event',
        'event_name': record.get('eventName', 'unknown'),
        'event_source': record.get('eventSource', 'unknown'),
        'source_ip': record.get('sourceIPAddress', 'unknown'),
        'user_agent': record.get('userAgent', 'unknown'),
        'user_identity': record.get('userIdentity', {}),
        'event_time': record.get('eventTime', datetime.now(timezone.utc).isoformat()),
        'aws_region': record.get('awsRegion', 'unknown'),
        'error_code': record.get('errorCode'),
        'error_message': record.get('errorMessage'),
        'read_only': record.get('readOnly', True),
        'resources': record.get('resources', [])
    }


def extract_source_ip_from_guardduty(detail: Dict[str, Any]) -> Optional[str]:
    """Extract source IP from GuardDuty finding detail."""
    service = detail.get('service', {})
    
    # Check various locations where IP might be stored
    if 'remoteIpDetails' in service:
        return service['remoteIpDetails'].get('ipAddressV4')
    
    if 'action' in service:
        action = service['action']
        if 'networkConnectionAction' in action:
            return action['networkConnectionAction'].get('remoteIpDetails', {}).get('ipAddressV4')
        if 'awsApiCallAction' in action:
            return action['awsApiCallAction'].get('remoteIpDetails', {}).get('ipAddressV4')
    
    return None


def extract_user_identity_from_guardduty(detail: Dict[str, Any]) -> Dict[str, Any]:
    """Extract user identity from GuardDuty finding detail."""
    service = detail.get('service', {})
    
    if 'action' in service and 'awsApiCallAction' in service['action']:
        return service['action']['awsApiCallAction'].get('userDetails', {})
    
    return {}


def calculate_risk_score(event: Dict[str, Any]) -> int:
    """
    Calculate risk score for a security event.
    
    Args:
        event: Processed security event
        
    Returns:
        Risk score from 0-100
    """
    score = 0
    
    # Base score from severity (GuardDuty)
    if 'severity' in event:
        score += min(event['severity'] * 10, 50)  # Max 50 points
    
    # Event type scoring
    high_risk_events = [
        'UnauthorizedAPICall',
        'InstanceCredentialExfiltration',
        'CryptoCurrency',
        'Stealth',
        'Backdoor'
    ]
    
    event_type = event.get('finding_type', event.get('event_name', ''))
    for risk_event in high_risk_events:
        if risk_event.lower() in event_type.lower():
            score += 30
            break
    
    # Source IP reputation
    if 'geo_info' in event and event['geo_info']:
        geo = event['geo_info']
        if geo.get('is_malicious', False):
            score += 25
        if geo.get('country') in ['CN', 'RU', 'KP']:  # High-risk countries
            score += 10
    
    # Time-based scoring (after hours)
    try:
        event_time = datetime.fromisoformat(event.get('event_time', '').replace('Z', '+00:00'))
        hour = event_time.hour
        if hour < 6 or hour > 22:  # After hours activity
            score += 5
    except:
        pass
    
    # Failed events are higher risk
    if event.get('error_code') or event.get('error_message'):
        score += 10
    
    return min(score, 100)  # Cap at 100


def enrich_ip_geolocation(ip_address: str) -> Dict[str, Any]:
    """
    Enrich IP address with geolocation data.
    
    Args:
        ip_address: IP address to lookup
        
    Returns:
        Geolocation information
    """
    # Placeholder for geolocation enrichment
    # In production, integrate with MaxMind GeoIP or similar service
    
    # Basic validation
    if not ip_address or ip_address in ['unknown', 'localhost', '127.0.0.1']:
        return {}
    
    # Mock enrichment for demonstration
    return {
        'ip': ip_address,
        'country': 'US',  # Would be actual lookup
        'city': 'Seattle',
        'latitude': 47.6062,
        'longitude': -122.3321,
        'is_malicious': False,  # Would check threat feeds
        'asn': 'AS16509',
        'organization': 'Amazon.com, Inc.'
    }


def check_threat_intelligence(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check event against threat intelligence feeds.
    
    Args:
        event: Security event to check
        
    Returns:
        Threat intelligence results
    """
    # Placeholder for threat intelligence integration
    # In production, integrate with threat feeds like AlienVault OTX, VirusTotal, etc.
    
    threat_info = {
        'is_known_threat': False,
        'threat_type': None,
        'confidence': 0,
        'sources': []
    }
    
    # Check IP reputation
    source_ip = event.get('source_ip')
    if source_ip and source_ip != 'unknown':
        # Mock threat check
        known_bad_ips = ['192.168.1.100', '10.0.0.50']  # Example bad IPs
        if source_ip in known_bad_ips:
            threat_info.update({
                'is_known_threat': True,
                'threat_type': 'malicious_ip',
                'confidence': 85,
                'sources': ['internal_blocklist']
            })
    
    return threat_info


def should_generate_alert(event: Dict[str, Any]) -> bool:
    """
    Determine if an event should generate an alert.
    
    Args:
        event: Processed security event
        
    Returns:
        True if alert should be generated
    """
    # Alert on high risk scores
    if event.get('risk_score', 0) >= 70:
        return True
    
    # Alert on high-severity GuardDuty findings
    if event.get('severity', 0) >= 7.0:
        return True
    
    # Alert on known threats
    if event.get('threat_intel', {}).get('is_known_threat', False):
        return True
    
    # Alert on specific event types
    critical_events = [
        'RootCredentialUsage',
        'UnauthorizedAPICall',
        'InstanceCredentialExfiltration'
    ]
    
    finding_type = event.get('finding_type', '')
    event_name = event.get('event_name', '')
    
    for critical_event in critical_events:
        if critical_event in finding_type or critical_event in event_name:
            return True
    
    return False


def generate_security_alert(event: Dict[str, Any]) -> None:
    """
    Generate and send security alert.
    
    Args:
        event: Security event to alert on
    """
    if not SNS_TOPIC_ARN:
        logger.warning("No SNS topic configured for alerts")
        return
    
    try:
        alert_message = {
            'alert_id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'severity': 'HIGH' if event.get('risk_score', 0) >= 80 else 'MEDIUM',
            'event_summary': {
                'event_id': event.get('event_id'),
                'event_type': event.get('event_type'),
                'risk_score': event.get('risk_score'),
                'source_ip': event.get('source_ip'),
                'finding_type': event.get('finding_type'),
                'account': event.get('account'),
                'region': event.get('region')
            },
            'recommendations': generate_recommendations(event)
        }
        
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(alert_message, indent=2),
            Subject=f"Security Alert: {event.get('finding_type', 'Unknown Event')}"
        )
        
        logger.info(f"Alert generated for event {event.get('event_id')}")
        
    except Exception as e:
        logger.error(f"Failed to send alert: {str(e)}")


def generate_recommendations(event: Dict[str, Any]) -> List[str]:
    """Generate security recommendations based on event type."""
    recommendations = []
    
    finding_type = event.get('finding_type', '').lower()
    
    if 'credential' in finding_type:
        recommendations.extend([
            "Immediately rotate affected credentials",
            "Review IAM policies for excessive permissions",
            "Enable AWS CloudTrail for API monitoring"
        ])
    
    if 'unauthorized' in finding_type:
        recommendations.extend([
            "Block source IP address if malicious",
            "Review network security groups",
            "Implement additional access controls"
        ])
    
    if 'cryptocurrency' in finding_type:
        recommendations.extend([
            "Terminate affected instances immediately",
            "Scan for malware and backdoors",
            "Review instance launch permissions"
        ])
    
    if not recommendations:
        recommendations = [
            "Review event details for context",
            "Check related events in timeframe",
            "Verify if activity was authorized"
        ]
    
    return recommendations


def store_event_in_s3(event: Dict[str, Any]) -> None:
    """
    Store processed event in S3 data lake.
    
    Args:
        event: Processed security event
    """
    try:
        # Generate S3 key with partitioning
        event_time = datetime.fromisoformat(event.get('event_time', '').replace('Z', '+00:00'))
        year = event_time.strftime('%Y')
        month = event_time.strftime('%m')
        day = event_time.strftime('%d')
        hour = event_time.strftime('%H')
        
        s3_key = f"security-events/year={year}/month={month}/day={day}/hour={hour}/{event.get('event_id')}.json"
        
        # Store as JSON (in production, consider Parquet for better query performance)
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(event, default=str),
            ContentType='application/json',
            ServerSideEncryption='AES256'
        )
        
        logger.debug(f"Stored event {event.get('event_id')} in S3: {s3_key}")
        
    except Exception as e:
        logger.error(f"Failed to store event in S3: {str(e)}")
        raise
