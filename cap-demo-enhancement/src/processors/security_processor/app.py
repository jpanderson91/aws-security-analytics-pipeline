#!/usr/bin/env python3
"""
CAP Demo - Security Event Processor
Processes security logs and alerts from Kafka topics
"""

import json
import os
import time
import logging
import boto3
from datetime import datetime, timezone
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import threading
import signal
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityEventProcessor:
    """
    Security Event Processor for CAP Demo
    
    Processes security logs from Kafka and performs:
    - Threat detection and classification
    - Anomaly detection
    - Data enrichment and normalization
    - Storage in S3 data lake
    """
    
    def __init__(self):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.consumer_group = os.getenv('CONSUMER_GROUP', 'security-processor-group')
        self.topic = os.getenv('KAFKA_TOPIC', 'security-logs')
        self.s3_bucket = os.getenv('S3_BUCKET', 'cap-demo-data-lake-bronze')
        self.lambda_function = os.getenv('ALERT_LAMBDA_FUNCTION', 'cap-demo-alert-generator')
        
        # AWS clients
        self.s3_client = boto3.client('s3')
        self.lambda_client = boto3.client('lambda')
        
        # Processing state
        self.running = True
        self.processed_count = 0
        self.alert_count = 0
        
        # Threat detection patterns
        self.threat_patterns = {
            'failed_login': ['authentication failed', 'login failed', 'invalid credentials'],
            'malware': ['virus detected', 'trojan', 'malware', 'suspicious file'],
            'network_anomaly': ['port scan', 'ddos', 'unusual traffic', 'network intrusion'],
            'privilege_escalation': ['admin access', 'privilege escalation', 'unauthorized access'],
            'data_exfiltration': ['large download', 'data export', 'file transfer', 'sensitive data']
        }
        
        logger.info(f"Security Event Processor initialized")
        logger.info(f"Kafka servers: {self.bootstrap_servers}")
        logger.info(f"Topic: {self.topic}")
        logger.info(f"S3 Bucket: {self.s3_bucket}")
    
    def setup_consumer(self):
        """Setup Kafka consumer with proper configuration"""
        try:
            consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.consumer_group,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
                consumer_timeout_ms=10000,
                security_protocol='SSL' if 'amazonaws.com' in self.bootstrap_servers else 'PLAINTEXT'
            )
            logger.info(f"Kafka consumer setup successful for topic: {self.topic}")
            return consumer
        except Exception as e:
            logger.error(f"Failed to setup Kafka consumer: {e}")
            raise
    
    def classify_threat(self, event_data):
        """
        Classify security events based on content analysis
        
        Args:
            event_data: Dict containing security event data
            
        Returns:
            Dict with threat classification and severity
        """
        try:
            event_text = json.dumps(event_data).lower()
            
            # Check for threat patterns
            detected_threats = []
            for threat_type, patterns in self.threat_patterns.items():
                for pattern in patterns:
                    if pattern in event_text:
                        detected_threats.append(threat_type)
                        break
            
            # Determine severity
            severity = 'low'
            if len(detected_threats) > 1:
                severity = 'high'
            elif detected_threats:
                severity = 'medium'
            
            # Calculate risk score
            risk_score = len(detected_threats) * 25
            if risk_score > 100:
                risk_score = 100
            
            return {
                'threats_detected': detected_threats,
                'severity': severity,
                'risk_score': risk_score,
                'classification_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in threat classification: {e}")
            return {
                'threats_detected': [],
                'severity': 'unknown',
                'risk_score': 0,
                'classification_timestamp': datetime.now(timezone.utc).isoformat(),
                'error': str(e)
            }
    
    def enrich_event(self, event_data, classification):
        """
        Enrich security event with additional context and metadata
        
        Args:
            event_data: Original event data
            classification: Threat classification results
            
        Returns:
            Enriched event data
        """
        try:
            enriched_event = {
                'original_event': event_data,
                'threat_analysis': classification,
                'processing_metadata': {
                    'processor': 'security-event-processor',
                    'processor_version': '1.0.0',
                    'processing_timestamp': datetime.now(timezone.utc).isoformat(),
                    'processing_time_ms': 0,  # Will be updated
                    'customer_id': event_data.get('customer_id', 'unknown'),
                    'event_id': f"sec_{int(time.time() * 1000)}_{self.processed_count}"
                },
                'data_lake_metadata': {
                    'layer': 'bronze',
                    'partition_date': datetime.now(timezone.utc).strftime('%Y/%m/%d'),
                    'partition_hour': datetime.now(timezone.utc).strftime('%H'),
                    'schema_version': '1.0'
                }
            }
            
            return enriched_event
            
        except Exception as e:
            logger.error(f"Error enriching event: {e}")
            return event_data
    
    def store_in_s3(self, enriched_event):
        """
        Store processed security event in S3 data lake
        
        Args:
            enriched_event: Enriched and classified event data
        """
        try:
            # Generate S3 key with partitioning
            date_partition = enriched_event['data_lake_metadata']['partition_date']
            hour_partition = enriched_event['data_lake_metadata']['partition_hour']
            event_id = enriched_event['processing_metadata']['event_id']
            
            s3_key = f"security-events/date={date_partition}/hour={hour_partition}/{event_id}.json"
            
            # Store in S3
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=json.dumps(enriched_event, indent=2),
                ContentType='application/json',
                Metadata={
                    'event-type': 'security-event',
                    'severity': enriched_event['threat_analysis']['severity'],
                    'risk-score': str(enriched_event['threat_analysis']['risk_score']),
                    'processor': 'security-event-processor'
                }
            )
            
            logger.debug(f"Stored event in S3: {s3_key}")
            return s3_key
            
        except Exception as e:
            logger.error(f"Error storing event in S3: {e}")
            return None
    
    def trigger_alert(self, enriched_event):
        """
        Trigger Lambda alert function for high-severity events
        
        Args:
            enriched_event: Enriched event data
        """
        try:
            severity = enriched_event['threat_analysis']['severity']
            risk_score = enriched_event['threat_analysis']['risk_score']
            
            # Only trigger alerts for medium/high severity events
            if severity in ['medium', 'high'] or risk_score > 50:
                alert_payload = {
                    'alert_type': 'security_threat',
                    'severity': severity,
                    'risk_score': risk_score,
                    'threats': enriched_event['threat_analysis']['threats_detected'],
                    'customer_id': enriched_event['processing_metadata']['customer_id'],
                    'event_id': enriched_event['processing_metadata']['event_id'],
                    'timestamp': enriched_event['processing_metadata']['processing_timestamp']
                }
                
                # Invoke Lambda function
                response = self.lambda_client.invoke(
                    FunctionName=self.lambda_function,
                    InvocationType='Event',  # Async invocation
                    Payload=json.dumps(alert_payload)
                )
                
                self.alert_count += 1
                logger.info(f"Alert triggered for event {enriched_event['processing_metadata']['event_id']}")
                
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    def process_event(self, event_data):
        """
        Process a single security event
        
        Args:
            event_data: Raw event data from Kafka
        """
        start_time = time.time()
        
        try:
            # Classify threats
            classification = self.classify_threat(event_data)
            
            # Enrich event
            enriched_event = self.enrich_event(event_data, classification)
            
            # Update processing time
            processing_time = (time.time() - start_time) * 1000
            enriched_event['processing_metadata']['processing_time_ms'] = round(processing_time, 2)
            
            # Store in S3
            s3_key = self.store_in_s3(enriched_event)
            
            # Trigger alerts if needed
            if classification['severity'] in ['medium', 'high']:
                self.trigger_alert(enriched_event)
            
            self.processed_count += 1
            
            if self.processed_count % 100 == 0:
                logger.info(f"Processed {self.processed_count} events, triggered {self.alert_count} alerts")
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
    
    def health_check(self):
        """
        Periodic health check reporting
        """
        while self.running:
            try:
                health_status = {
                    'processor': 'security-event-processor',
                    'status': 'healthy' if self.running else 'stopped',
                    'processed_events': self.processed_count,
                    'alerts_generated': self.alert_count,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'uptime_seconds': time.time() - self.start_time
                }
                
                logger.info(f"Health check: {json.dumps(health_status)}")
                
                # Sleep for 60 seconds
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                time.sleep(60)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def run(self):
        """
        Main processing loop
        """
        self.start_time = time.time()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Start health check thread
        health_thread = threading.Thread(target=self.health_check, daemon=True)
        health_thread.start()
        
        logger.info("Starting Security Event Processor...")
        
        try:
            # Setup Kafka consumer
            consumer = self.setup_consumer()
            
            # Main processing loop
            for message in consumer:
                if not self.running:
                    break
                
                try:
                    if message.value:
                        self.process_event(message.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            logger.info(f"Shutting down. Processed {self.processed_count} events, generated {self.alert_count} alerts")
            self.running = False

def main():
    """Main entry point"""
    processor = SecurityEventProcessor()
    processor.run()

if __name__ == "__main__":
    main()
