"""
CAP Demo - Data Validator Lambda Function
Validates incoming data and moves it from Bronze to Silver bucket
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

def lambda_handler(event, context):
    """
    Main Lambda handler function
    Validates data in Bronze bucket and moves valid data to Silver bucket
    """
    
    try:
        # Log the incoming event
        logger.info(f"Processing event: {json.dumps(event)}")
        
        # Process S3 event records
        for record in event.get('Records', []):
            if record.get('eventSource') == 'aws:s3':
                bucket_name = record['s3']['bucket']['name']
                object_key = record['s3']['object']['key']
                
                logger.info(f"Processing file: {object_key} from bucket: {bucket_name}")
                
                # Validate and process the file
                result = validate_and_process_file(bucket_name, object_key)
                
                if result['success']:
                    logger.info(f"Successfully processed {object_key}")
                else:
                    logger.error(f"Failed to process {object_key}: {result['error']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data validation completed successfully',
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }

def validate_and_process_file(bucket_name, object_key):
    """
    Validate file contents and move to Silver bucket if valid
    """
    
    try:
        # Download file from Bronze bucket
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read()
        
        # Basic validation - check if it's valid JSON
        try:
            data = json.loads(file_content)
            logger.info(f"File {object_key} contains valid JSON with {len(data)} records")
        except json.JSONDecodeError:
            logger.warning(f"File {object_key} is not valid JSON, treating as text")
            data = file_content.decode('utf-8')
        
        # TODO: Add more sophisticated validation logic here
        # For now, we'll consider all files as valid
        
        # Move to Silver bucket (placeholder - would need actual Silver bucket name)
        silver_bucket = "${silver_bucket}"
        if silver_bucket and silver_bucket != "SILVER_BUCKET_PLACEHOLDER":
            silver_key = f"validated/{object_key}"
            s3_client.copy_object(
                CopySource={'Bucket': bucket_name, 'Key': object_key},
                Bucket=silver_bucket,
                Key=silver_key
            )
            logger.info(f"Copied {object_key} to {silver_bucket}/{silver_key}")
        
        return {
            'success': True,
            'processed_records': len(data) if isinstance(data, list) else 1
        }
        
    except Exception as e:
        logger.error(f"Error validating file {object_key}: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def validate_security_event(event_data):
    """
    Validate security event data structure
    """
    
    required_fields = ['timestamp', 'event_type', 'source', 'severity']
    
    for field in required_fields:
        if field not in event_data:
            return False, f"Missing required field: {field}"
    
    # Validate timestamp format
    try:
        datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00'))
    except ValueError:
        return False, "Invalid timestamp format"
    
    # Validate severity level
    valid_severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    if event_data['severity'] not in valid_severities:
        return False, f"Invalid severity level: {event_data['severity']}"
    
    return True, "Valid"

if __name__ == "__main__":
    # Test function locally
    test_event = {
        "Records": [
            {
                "eventSource": "aws:s3",
                "s3": {
                    "bucket": {"name": "test-bronze-bucket"},
                    "object": {"key": "test-data.json"}
                }
            }
        ]
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
