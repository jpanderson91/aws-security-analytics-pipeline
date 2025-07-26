"""
CAP Demo - Analytics Trigger Lambda Function
Triggers analytics processing when data is added to Silver bucket
"""

import json
import boto3
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
athena_client = boto3.client('athena')

def lambda_handler(event, context):
    """
    Main Lambda handler function
    Triggers analytics processing when new data arrives in Silver bucket
    """
    
    try:
        # Log the incoming event
        logger.info("Processing analytics trigger event: %s", json.dumps(event))
        
        # Process S3 event records
        for record in event.get('Records', []):
            if record.get('eventSource') == 'aws:s3':
                bucket_name = record['s3']['bucket']['name']
                object_key = record['s3']['object']['key']
                
                logger.info("Processing analytics for file: %s from bucket: %s", object_key, bucket_name)
                
                # Trigger analytics processing
                result = trigger_analytics_processing(bucket_name, object_key)
                
                if result['success']:
                    logger.info("Successfully triggered analytics for %s", object_key)
                else:
                    logger.error("Failed to trigger analytics for %s: %s", object_key, result['error'])
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Analytics processing triggered successfully',
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        logger.error("Error processing analytics trigger: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }

def trigger_analytics_processing(bucket_name, object_key):
    """
    Trigger analytics processing for the specified file
    """
    
    try:
        # Process the file and create aggregated analytics data
        analytics_data = process_analytics_data(bucket_name, object_key)
        
        # Store results in Gold bucket
        gold_bucket = "${gold_bucket}"
        if gold_bucket and gold_bucket != "GOLD_BUCKET_PLACEHOLDER":
            gold_key = f"analytics/{datetime.utcnow().strftime('%Y/%m/%d')}/{object_key}"
            
            s3_client.put_object(
                Bucket=gold_bucket,
                Key=gold_key,
                Body=json.dumps(analytics_data),
                ContentType='application/json'
            )
            
            logger.info("Stored analytics results in %s/%s", gold_bucket, gold_key)
        
        return {
            'success': True,
            'analytics_records': len(analytics_data.get('metrics', []))
        }
        
    except Exception as e:
        logger.error("Error triggering analytics for %s: %s", object_key, str(e))
        return {
            'success': False,
            'error': str(e)
        }

def process_analytics_data(bucket_name, object_key):
    """
    Process the data file and generate analytics metrics
    """
    
    try:
        # Download file from Silver bucket
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read()
        
        # Parse the data
        try:
            data = json.loads(file_content)
        except json.JSONDecodeError:
            logger.warning("File %s is not JSON, skipping analytics", object_key)
            return {'metrics': []}
        
        # Generate analytics metrics
        analytics_data = {
            'source_file': object_key,
            'processed_at': datetime.utcnow().isoformat(),
            'metrics': generate_security_metrics(data)
        }
        
        return analytics_data
        
    except Exception as e:
        logger.error("Error processing analytics data for %s: %s", object_key, str(e))
        raise

def generate_security_metrics(data):
    """
    Generate security analytics metrics from the data
    """
    
    metrics = []
    
    try:
        if isinstance(data, list):
            # Count events by type
            event_counts = {}
            severity_counts = {}
            
            for event in data:
                if isinstance(event, dict):
                    event_type = event.get('event_type', 'unknown')
                    severity = event.get('severity', 'unknown')
                    
                    event_counts[event_type] = event_counts.get(event_type, 0) + 1
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Create metrics
            for event_type, count in event_counts.items():
                metrics.append({
                    'metric_type': 'event_count',
                    'event_type': event_type,
                    'count': count,
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            for severity, count in severity_counts.items():
                metrics.append({
                    'metric_type': 'severity_count',
                    'severity': severity,
                    'count': count,
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        logger.info("Generated %d analytics metrics", len(metrics))
        return metrics
        
    except Exception as e:
        logger.error("Error generating metrics: %s", str(e))
        return []

if __name__ == "__main__":
    # Test function locally
    test_event = {
        "Records": [
            {
                "eventSource": "aws:s3",
                "s3": {
                    "bucket": {"name": "test-silver-bucket"},
                    "object": {"key": "validated/test-data.json"}
                }
            }
        ]
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
