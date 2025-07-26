"""
CAP Demo - Customer Notifier Lambda Function
Sends notifications to customers about security events
"""

import json
import boto3
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
sns_client = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Main Lambda handler function
    Processes customer notifications for security events
    """
    
    try:
        # Log the incoming event
        logger.info("Processing customer notification event: %s", json.dumps(event))
        
        # Process different event sources
        if 'Records' in event:
            # S3 or DynamoDB event
            for record in event['Records']:
                if record.get('eventSource') == 'aws:s3':
                    process_s3_notification(record)
                elif record.get('eventSource') == 'aws:dynamodb':
                    process_dynamodb_notification(record)
        else:
            # Direct invocation
            process_direct_notification(event)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Customer notifications processed successfully',
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        logger.error("Error processing customer notifications: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }

def process_s3_notification(record):
    """
    Process S3 event for customer notification
    """
    
    bucket_name = record['s3']['bucket']['name']
    object_key = record['s3']['object']['key']
    
    logger.info("Processing S3 notification for %s/%s", bucket_name, object_key)
    
    # TODO: Implement S3-based notification logic
    # For now, just log the event
    logger.info("S3 notification processed for %s", object_key)

def process_dynamodb_notification(record):
    """
    Process DynamoDB event for customer notification
    """
    
    event_name = record.get('eventName')
    logger.info("Processing DynamoDB notification for event: %s", event_name)
    
    # TODO: Implement DynamoDB-based notification logic
    # For now, just log the event
    logger.info("DynamoDB notification processed for %s", event_name)

def process_direct_notification(event):
    """
    Process direct invocation notification
    """
    
    notification_type = event.get('notification_type', 'general')
    customer_id = event.get('customer_id')
    message = event.get('message', 'Security event notification')
    
    logger.info("Processing direct notification for customer %s", customer_id)
    
    if customer_id:
        send_customer_notification(customer_id, notification_type, message)
    else:
        logger.warning("No customer_id provided for direct notification")

def send_customer_notification(customer_id, notification_type, message):
    """
    Send notification to a specific customer
    """
    
    try:
        # Get customer notification preferences (placeholder)
        customer_prefs = get_customer_preferences(customer_id)
        
        if customer_prefs.get('email_notifications', True):
            send_email_notification(customer_id, notification_type, message)
        
        if customer_prefs.get('sms_notifications', False):
            send_sms_notification(customer_id, notification_type, message)
        
        # Log the notification
        log_notification(customer_id, notification_type, message)
        
        logger.info("Notification sent to customer %s", customer_id)
        
    except Exception as e:
        logger.error("Error sending notification to customer %s: %s", customer_id, str(e))

def get_customer_preferences(customer_id):
    """
    Get customer notification preferences from DynamoDB
    """
    
    try:
        # Placeholder - would query DynamoDB for real preferences
        return {
            'email_notifications': True,
            'sms_notifications': False,
            'severity_threshold': 'MEDIUM'
        }
    except Exception as e:
        logger.error("Error getting customer preferences for %s: %s", customer_id, str(e))
        return {}

def send_email_notification(customer_id, notification_type, message):
    """
    Send email notification via SNS
    """
    
    try:
        # Placeholder SNS topic ARN
        topic_arn = f"arn:aws:sns:us-east-1:123456789012:customer-notifications-{customer_id}"
        
        sns_message = {
            'customer_id': customer_id,
            'notification_type': notification_type,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Note: In a real implementation, you would actually publish to SNS
        logger.info("Would send email notification to customer %s via SNS", customer_id)
        
    except Exception as e:
        logger.error("Error sending email notification: %s", str(e))

def send_sms_notification(customer_id, notification_type, message):
    """
    Send SMS notification via SNS
    """
    
    try:
        # Note: In a real implementation, you would send SMS via SNS
        logger.info("Would send SMS notification to customer %s", customer_id)
        
    except Exception as e:
        logger.error("Error sending SMS notification: %s", str(e))

def log_notification(customer_id, notification_type, message):
    """
    Log notification to DynamoDB for audit trail
    """
    
    try:
        # Placeholder - would log to DynamoDB table
        notification_record = {
            'customer_id': customer_id,
            'notification_type': notification_type,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'sent'
        }
        
        logger.info("Notification logged for customer %s", customer_id)
        
    except Exception as e:
        logger.error("Error logging notification: %s", str(e))

if __name__ == "__main__":
    # Test function locally
    test_event = {
        "customer_id": "12345",
        "notification_type": "security_alert",
        "message": "High severity security event detected"
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
