"""
CAP Demo - Alert Generator Lambda Function
Processes security and metrics alerts from ECS processors
"""

import json
import boto3
import logging
from datetime import datetime, timezone
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
sns_client = boto3.client('sns')
ses_client = boto3.client('ses')
cloudwatch_client = boto3.client('cloudwatch')

def lambda_handler(event, context):
    """
    Main Lambda handler for processing alerts
    
    Args:
        event: Alert data from ECS processors
        context: Lambda context
        
    Returns:
        Response with alert processing status
    """
    
    try:
        logger.info(f"Processing alert: {json.dumps(event)}")
        
        alert_type = event.get('alert_type', 'unknown')
        severity = event.get('severity', 'low')
        customer_id = event.get('customer_id', 'unknown')
        
        # Process different alert types
        if alert_type == 'security_threat':
            response = process_security_alert(event)
        elif alert_type == 'performance_anomaly':
            response = process_performance_alert(event)
        elif alert_type == 'customer_notification':
            response = process_customer_notification(event)
        else:
            response = process_generic_alert(event)
        
        # Send CloudWatch metric
        send_cloudwatch_metric(alert_type, severity, customer_id)
        
        logger.info(f"Alert processed successfully: {response}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Alert processed successfully',
                'alert_id': response.get('alert_id'),
                'actions_taken': response.get('actions_taken', [])
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing alert: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Alert processing failed',
                'message': str(e)
            })
        }

def process_security_alert(event):
    """
    Process security threat alerts
    
    Args:
        event: Security alert data
        
    Returns:
        Processing response
    """
    
    try:
        severity = event.get('severity', 'low')
        risk_score = event.get('risk_score', 0)
        threats = event.get('threats', [])
        customer_id = event.get('customer_id', 'unknown')
        event_id = event.get('event_id', 'unknown')
        
        actions_taken = []
        
        # Generate alert message
        alert_message = generate_security_alert_message(event)
        
        # Determine notification channels based on severity
        if severity == 'critical' or risk_score > 80:
            # High priority: SNS + Email + Slack
            actions_taken.extend([
                send_sns_notification(alert_message, 'CRITICAL'),
                send_email_notification(alert_message, customer_id, 'CRITICAL'),
                create_incident_ticket(event)
            ])
            
        elif severity == 'high' or risk_score > 60:
            # Medium priority: SNS + Email
            actions_taken.extend([
                send_sns_notification(alert_message, 'HIGH'),
                send_email_notification(alert_message, customer_id, 'HIGH')
            ])
            
        else:
            # Low priority: SNS only
            actions_taken.append(
                send_sns_notification(alert_message, 'MEDIUM')
            )
        
        # Store alert in DynamoDB for tracking
        alert_record = store_alert_record({
            'alert_id': f"sec_{int(datetime.now(timezone.utc).timestamp())}",
            'alert_type': 'security_threat',
            'customer_id': customer_id,
            'severity': severity,
            'risk_score': risk_score,
            'threats_detected': threats,
            'event_id': event_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'actions_taken': actions_taken
        })
        
        return {
            'alert_id': alert_record['alert_id'],
            'actions_taken': actions_taken,
            'severity': severity,
            'risk_score': risk_score
        }
        
    except Exception as e:
        logger.error(f"Error processing security alert: {e}")
        raise

def process_performance_alert(event):
    """
    Process performance anomaly alerts
    
    Args:
        event: Performance alert data
        
    Returns:
        Processing response
    """
    
    try:
        metric_type = event.get('metric_type', 'unknown')
        anomaly_severity = event.get('anomaly_severity', 'low')
        z_score = event.get('z_score', 0)
        customer_id = event.get('customer_id', 'unknown')
        
        actions_taken = []
        
        # Generate alert message
        alert_message = generate_performance_alert_message(event)
        
        # Notification logic for performance alerts
        if anomaly_severity == 'critical' or z_score > 3:
            actions_taken.extend([
                send_sns_notification(alert_message, 'PERFORMANCE_CRITICAL'),
                send_email_notification(alert_message, customer_id, 'PERFORMANCE'),
                trigger_auto_scaling(customer_id, metric_type)
            ])
            
        elif anomaly_severity == 'high' or z_score > 2:
            actions_taken.extend([
                send_sns_notification(alert_message, 'PERFORMANCE_HIGH'),
                send_email_notification(alert_message, customer_id, 'PERFORMANCE')
            ])
        
        # Store alert record
        alert_record = store_alert_record({
            'alert_id': f"perf_{int(datetime.now(timezone.utc).timestamp())}",
            'alert_type': 'performance_anomaly',
            'customer_id': customer_id,
            'severity': anomaly_severity,
            'metric_type': metric_type,
            'z_score': z_score,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'actions_taken': actions_taken
        })
        
        return {
            'alert_id': alert_record['alert_id'],
            'actions_taken': actions_taken,
            'severity': anomaly_severity
        }
        
    except Exception as e:
        logger.error(f"Error processing performance alert: {e}")
        raise

def process_customer_notification(event):
    """
    Process customer workflow notifications
    
    Args:
        event: Customer notification data
        
    Returns:
        Processing response
    """
    
    try:
        notification_type = event.get('notification_type', 'general')
        customer_id = event.get('customer_id', 'unknown')
        message = event.get('message', 'Customer notification')
        
        actions_taken = []
        
        # Send appropriate notifications
        if notification_type == 'onboarding_complete':
            actions_taken.append(
                send_welcome_email(customer_id, event.get('onboarding_data', {}))
            )
        elif notification_type == 'sla_breach':
            actions_taken.extend([
                send_sla_notification(customer_id, event),
                create_sla_ticket(event)
            ])
        else:
            actions_taken.append(
                send_generic_notification(customer_id, message)
            )
        
        # Store notification record
        alert_record = store_alert_record({
            'alert_id': f"notif_{int(datetime.now(timezone.utc).timestamp())}",
            'alert_type': 'customer_notification',
            'customer_id': customer_id,
            'notification_type': notification_type,
            'message': message,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'actions_taken': actions_taken
        })
        
        return {
            'alert_id': alert_record['alert_id'],
            'actions_taken': actions_taken,
            'notification_type': notification_type
        }
        
    except Exception as e:
        logger.error(f"Error processing customer notification: {e}")
        raise

def process_generic_alert(event):
    """
    Process generic alerts
    
    Args:
        event: Generic alert data
        
    Returns:
        Processing response
    """
    
    try:
        alert_message = f"Generic alert: {json.dumps(event)}"
        
        actions_taken = [
            send_sns_notification(alert_message, 'GENERIC')
        ]
        
        alert_record = store_alert_record({
            'alert_id': f"generic_{int(datetime.now(timezone.utc).timestamp())}",
            'alert_type': 'generic',
            'data': event,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'actions_taken': actions_taken
        })
        
        return {
            'alert_id': alert_record['alert_id'],
            'actions_taken': actions_taken
        }
        
    except Exception as e:
        logger.error(f"Error processing generic alert: {e}")
        raise

def generate_security_alert_message(event):
    """Generate formatted security alert message"""
    
    severity = event.get('severity', 'unknown')
    risk_score = event.get('risk_score', 0)
    threats = event.get('threats', [])
    customer_id = event.get('customer_id', 'unknown')
    event_id = event.get('event_id', 'unknown')
    
    message = f"""
🚨 SECURITY ALERT - {severity.upper()} SEVERITY

Customer: {customer_id}
Event ID: {event_id}
Risk Score: {risk_score}/100
Threats Detected: {', '.join(threats) if threats else 'Unknown'}
Timestamp: {datetime.now(timezone.utc).isoformat()}

Immediate action may be required for high-severity threats.
Check the security dashboard for detailed analysis.
"""
    
    return message.strip()

def generate_performance_alert_message(event):
    """Generate formatted performance alert message"""
    
    metric_type = event.get('metric_type', 'unknown')
    anomaly_severity = event.get('anomaly_severity', 'unknown')
    z_score = event.get('z_score', 0)
    customer_id = event.get('customer_id', 'unknown')
    current_value = event.get('current_value', 'unknown')
    
    message = f"""
📊 PERFORMANCE ALERT - {anomaly_severity.upper()}

Customer: {customer_id}
Metric: {metric_type}
Current Value: {current_value}
Anomaly Score: {z_score}
Timestamp: {datetime.now(timezone.utc).isoformat()}

Performance metrics have deviated from baseline.
Check the metrics dashboard for trend analysis.
"""
    
    return message.strip()

def send_sns_notification(message, priority):
    """Send SNS notification"""
    
    try:
        topic_arn = os.getenv('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-1:123456789012:cap-demo-alerts')
        
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=f"CAP Demo Alert - {priority}",
            MessageAttributes={
                'priority': {
                    'DataType': 'String',
                    'StringValue': priority
                }
            }
        )
        
        logger.info(f"SNS notification sent: {response['MessageId']}")
        return f"SNS notification sent: {response['MessageId']}"
        
    except Exception as e:
        logger.error(f"Error sending SNS notification: {e}")
        return f"SNS error: {str(e)}"

def send_email_notification(message, customer_id, alert_type):
    """Send email notification"""
    
    try:
        from_email = os.getenv('FROM_EMAIL', 'alerts@cap-demo.aws')
        to_email = os.getenv('TO_EMAIL', f'{customer_id}@cap-demo.aws')
        
        response = ses_client.send_email(
            Source=from_email,
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': f'CAP Demo Alert - {alert_type}'},
                'Body': {'Text': {'Data': message}}
            }
        )
        
        logger.info(f"Email sent: {response['MessageId']}")
        return f"Email sent: {response['MessageId']}"
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return f"Email error: {str(e)}"

def send_cloudwatch_metric(alert_type, severity, customer_id):
    """Send CloudWatch custom metric"""
    
    try:
        cloudwatch_client.put_metric_data(
            Namespace='CAP-Demo/Alerts',
            MetricData=[
                {
                    'MetricName': 'AlertsGenerated',
                    'Dimensions': [
                        {'Name': 'AlertType', 'Value': alert_type},
                        {'Name': 'Severity', 'Value': severity},
                        {'Name': 'Customer', 'Value': customer_id}
                    ],
                    'Value': 1,
                    'Unit': 'Count',
                    'Timestamp': datetime.now(timezone.utc)
                }
            ]
        )
        
        logger.info(f"CloudWatch metric sent for {alert_type}")
        
    except Exception as e:
        logger.error(f"Error sending CloudWatch metric: {e}")

def store_alert_record(alert_data):
    """Store alert record in DynamoDB"""
    
    try:
        dynamodb = boto3.resource('dynamodb')
        table_name = os.getenv('DYNAMODB_TABLE', 'cap-demo-alerts')
        table = dynamodb.Table(table_name)
        
        table.put_item(Item=alert_data)
        
        logger.info(f"Alert record stored: {alert_data['alert_id']}")
        return alert_data
        
    except Exception as e:
        logger.error(f"Error storing alert record: {e}")
        return alert_data

# Placeholder functions for advanced features
def create_incident_ticket(event):
    """Create incident ticket for critical alerts"""
    return "Incident ticket created (placeholder)"

def trigger_auto_scaling(customer_id, metric_type):
    """Trigger auto-scaling for performance issues"""
    return "Auto-scaling triggered (placeholder)"

def send_welcome_email(customer_id, onboarding_data):
    """Send welcome email for new customers"""
    return "Welcome email sent (placeholder)"

def send_sla_notification(customer_id, event):
    """Send SLA breach notification"""
    return "SLA notification sent (placeholder)"

def create_sla_ticket(event):
    """Create SLA breach ticket"""
    return "SLA ticket created (placeholder)"

def send_generic_notification(customer_id, message):
    """Send generic notification"""
    return "Generic notification sent (placeholder)"
