#!/usr/bin/env python3
"""
CAP Demo - Application Metrics Processor
Processes application performance metrics from Kafka topics
"""

import json
import os
import time
import logging
import boto3
import statistics
from datetime import datetime, timezone, timedelta
from kafka import KafkaConsumer
import threading
import signal
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetricsProcessor:
    """
    Application Metrics Processor for CAP Demo
    
    Processes application metrics from Kafka and performs:
    - Real-time aggregations (avg, min, max, percentiles)
    - Trend analysis and anomaly detection
    - Performance baseline calculations
    - Storage in S3 data lake (Bronze/Silver layers)
    """
    
    def __init__(self):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.consumer_group = os.getenv('CONSUMER_GROUP', 'metrics-processor-group')
        self.topic = os.getenv('KAFKA_TOPIC', 'application-metrics')
        self.s3_bucket_bronze = os.getenv('S3_BUCKET_BRONZE', 'cap-demo-data-lake-bronze')
        self.s3_bucket_silver = os.getenv('S3_BUCKET_SILVER', 'cap-demo-data-lake-silver')
        
        # AWS clients
        self.s3_client = boto3.client('s3')
        
        # Processing state
        self.running = True
        self.processed_count = 0
        self.aggregation_count = 0
        
        # Metrics windows for real-time aggregation
        self.metrics_windows = {
            '1min': deque(maxlen=60),    # 1-minute window
            '5min': deque(maxlen=300),   # 5-minute window
            '15min': deque(maxlen=900)   # 15-minute window
        }
        
        # Metrics storage by customer and metric type
        self.customer_metrics = defaultdict(lambda: defaultdict(list))
        self.baseline_metrics = defaultdict(dict)
        
        logger.info(f"Metrics Processor initialized")
        logger.info(f"Kafka servers: {self.bootstrap_servers}")
        logger.info(f"Topic: {self.topic}")
    
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
    
    def calculate_aggregations(self, metrics_data):
        """
        Calculate real-time aggregations for metrics
        
        Args:
            metrics_data: List of metric values
            
        Returns:
            Dict with aggregated statistics
        """
        try:
            if not metrics_data:
                return {}
            
            values = [float(m.get('value', 0)) for m in metrics_data if m.get('value') is not None]
            
            if not values:
                return {}
            
            aggregations = {
                'count': len(values),
                'sum': sum(values),
                'avg': statistics.mean(values),
                'min': min(values),
                'max': max(values),
                'median': statistics.median(values)
            }
            
            # Calculate percentiles if we have enough data
            if len(values) >= 10:
                sorted_values = sorted(values)
                aggregations.update({
                    'p50': statistics.median(sorted_values),
                    'p90': sorted_values[int(len(sorted_values) * 0.9)],
                    'p95': sorted_values[int(len(sorted_values) * 0.95)],
                    'p99': sorted_values[int(len(sorted_values) * 0.99)]
                })
            
            # Calculate standard deviation
            if len(values) > 1:
                aggregations['stddev'] = statistics.stdev(values)
            
            return aggregations
            
        except Exception as e:
            logger.error(f"Error calculating aggregations: {e}")
            return {}
    
    def detect_anomalies(self, current_metric, customer_id, metric_type):
        """
        Detect anomalies based on historical baselines
        
        Args:
            current_metric: Current metric value
            customer_id: Customer identifier
            metric_type: Type of metric (response_time, error_rate, etc.)
            
        Returns:
            Dict with anomaly analysis
        """
        try:
            current_value = float(current_metric.get('value', 0))
            
            # Get baseline for this customer and metric type
            baseline_key = f"{customer_id}_{metric_type}"
            baseline = self.baseline_metrics.get(baseline_key, {})
            
            if not baseline:
                return {
                    'is_anomaly': False,
                    'severity': 'normal',
                    'baseline_available': False
                }
            
            baseline_avg = baseline.get('avg', current_value)
            baseline_stddev = baseline.get('stddev', 0)
            
            # Calculate z-score
            if baseline_stddev > 0:
                z_score = abs(current_value - baseline_avg) / baseline_stddev
            else:
                z_score = 0
            
            # Determine anomaly severity
            if z_score > 3:
                severity = 'critical'
                is_anomaly = True
            elif z_score > 2:
                severity = 'high'
                is_anomaly = True
            elif z_score > 1.5:
                severity = 'medium'
                is_anomaly = True
            else:
                severity = 'normal'
                is_anomaly = False
            
            return {
                'is_anomaly': is_anomaly,
                'severity': severity,
                'z_score': round(z_score, 3),
                'baseline_avg': baseline_avg,
                'baseline_stddev': baseline_stddev,
                'current_value': current_value,
                'deviation_percent': round(abs(current_value - baseline_avg) / baseline_avg * 100, 2) if baseline_avg > 0 else 0,
                'baseline_available': True
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return {
                'is_anomaly': False,
                'severity': 'unknown',
                'error': str(e)
            }
    
    def update_baseline(self, customer_id, metric_type, metric_value):
        """
        Update baseline metrics for anomaly detection
        
        Args:
            customer_id: Customer identifier
            metric_type: Type of metric
            metric_value: Current metric value
        """
        try:
            baseline_key = f"{customer_id}_{metric_type}"
            
            # Add to customer metrics history
            self.customer_metrics[customer_id][metric_type].append({
                'value': float(metric_value),
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Keep only last 1000 values for baseline calculation
            if len(self.customer_metrics[customer_id][metric_type]) > 1000:
                self.customer_metrics[customer_id][metric_type] = \
                    self.customer_metrics[customer_id][metric_type][-1000:]
            
            # Recalculate baseline if we have enough data
            if len(self.customer_metrics[customer_id][metric_type]) >= 50:
                values = [m['value'] for m in self.customer_metrics[customer_id][metric_type]]
                
                self.baseline_metrics[baseline_key] = {
                    'avg': statistics.mean(values),
                    'stddev': statistics.stdev(values) if len(values) > 1 else 0,
                    'min': min(values),
                    'max': max(values),
                    'last_updated': datetime.now(timezone.utc).isoformat(),
                    'sample_count': len(values)
                }
            
        except Exception as e:
            logger.error(f"Error updating baseline: {e}")
    
    def process_metric(self, metric_data):
        """
        Process a single application metric
        
        Args:
            metric_data: Raw metric data from Kafka
        """
        start_time = time.time()
        
        try:
            customer_id = metric_data.get('customer_id', 'unknown')
            metric_type = metric_data.get('metric_type', 'unknown')
            metric_value = metric_data.get('value', 0)
            
            # Add to rolling windows
            current_time = datetime.now(timezone.utc)
            windowed_metric = {
                **metric_data,
                'processing_timestamp': current_time.isoformat()
            }
            
            for window_name, window_data in self.metrics_windows.items():
                window_data.append(windowed_metric)
            
            # Detect anomalies
            anomaly_analysis = self.detect_anomalies(metric_data, customer_id, metric_type)
            
            # Update baseline metrics
            self.update_baseline(customer_id, metric_type, metric_value)
            
            # Create enriched metric
            enriched_metric = {
                'original_metric': metric_data,
                'anomaly_analysis': anomaly_analysis,
                'processing_metadata': {
                    'processor': 'metrics-processor',
                    'processor_version': '1.0.0',
                    'processing_timestamp': current_time.isoformat(),
                    'processing_time_ms': round((time.time() - start_time) * 1000, 2),
                    'customer_id': customer_id,
                    'metric_type': metric_type,
                    'metric_id': f"metric_{int(time.time() * 1000)}_{self.processed_count}"
                },
                'data_lake_metadata': {
                    'layer': 'bronze',
                    'partition_date': current_time.strftime('%Y/%m/%d'),
                    'partition_hour': current_time.strftime('%H'),
                    'schema_version': '1.0'
                }
            }
            
            # Store in Bronze layer
            self.store_in_s3_bronze(enriched_metric)
            
            self.processed_count += 1
            
            if self.processed_count % 100 == 0:
                logger.info(f"Processed {self.processed_count} metrics, {self.aggregation_count} aggregations")
            
        except Exception as e:
            logger.error(f"Error processing metric: {e}")
    
    def store_in_s3_bronze(self, enriched_metric):
        """
        Store raw processed metric in S3 Bronze layer
        
        Args:
            enriched_metric: Enriched metric data
        """
        try:
            # Generate S3 key with partitioning
            date_partition = enriched_metric['data_lake_metadata']['partition_date']
            hour_partition = enriched_metric['data_lake_metadata']['partition_hour']
            customer_id = enriched_metric['processing_metadata']['customer_id']
            metric_id = enriched_metric['processing_metadata']['metric_id']
            
            s3_key = f"application-metrics/date={date_partition}/hour={hour_partition}/customer={customer_id}/{metric_id}.json"
            
            # Store in S3 Bronze
            self.s3_client.put_object(
                Bucket=self.s3_bucket_bronze,
                Key=s3_key,
                Body=json.dumps(enriched_metric, indent=2),
                ContentType='application/json',
                Metadata={
                    'event-type': 'application-metric',
                    'customer-id': customer_id,
                    'metric-type': enriched_metric['processing_metadata']['metric_type'],
                    'processor': 'metrics-processor'
                }
            )
            
            logger.debug(f"Stored metric in S3 Bronze: {s3_key}")
            
        except Exception as e:
            logger.error(f"Error storing metric in S3 Bronze: {e}")
    
    def generate_aggregations(self):
        """
        Generate and store aggregated metrics periodically
        """
        while self.running:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Generate aggregations for each window
                for window_name, window_data in self.metrics_windows.items():
                    if len(window_data) < 10:  # Need minimum data
                        continue
                    
                    # Group by customer and metric type
                    customer_groups = defaultdict(lambda: defaultdict(list))
                    
                    for metric in window_data:
                        customer_id = metric.get('customer_id', 'unknown')
                        metric_type = metric.get('metric_type', 'unknown')
                        customer_groups[customer_id][metric_type].append(metric)
                    
                    # Calculate aggregations for each group
                    for customer_id, metric_types in customer_groups.items():
                        for metric_type, metrics in metric_types.items():
                            
                            aggregations = self.calculate_aggregations(metrics)
                            
                            if aggregations:
                                aggregated_metric = {
                                    'aggregation_metadata': {
                                        'window': window_name,
                                        'customer_id': customer_id,
                                        'metric_type': metric_type,
                                        'aggregation_timestamp': current_time.isoformat(),
                                        'sample_count': len(metrics),
                                        'window_start': (current_time - timedelta(minutes=int(window_name.replace('min', '')))).isoformat(),
                                        'window_end': current_time.isoformat()
                                    },
                                    'aggregations': aggregations,
                                    'data_lake_metadata': {
                                        'layer': 'silver',
                                        'partition_date': current_time.strftime('%Y/%m/%d'),
                                        'partition_hour': current_time.strftime('%H'),
                                        'schema_version': '1.0'
                                    }
                                }
                                
                                self.store_aggregation_s3_silver(aggregated_metric)
                                self.aggregation_count += 1
                
                # Sleep for aggregation interval (every 60 seconds)
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error generating aggregations: {e}")
                time.sleep(60)
    
    def store_aggregation_s3_silver(self, aggregated_metric):
        """
        Store aggregated metrics in S3 Silver layer
        
        Args:
            aggregated_metric: Aggregated metric data
        """
        try:
            # Generate S3 key
            date_partition = aggregated_metric['data_lake_metadata']['partition_date']
            hour_partition = aggregated_metric['data_lake_metadata']['partition_hour']
            window = aggregated_metric['aggregation_metadata']['window']
            customer_id = aggregated_metric['aggregation_metadata']['customer_id']
            metric_type = aggregated_metric['aggregation_metadata']['metric_type']
            
            timestamp = int(datetime.now(timezone.utc).timestamp())
            s3_key = f"aggregated-metrics/date={date_partition}/hour={hour_partition}/window={window}/customer={customer_id}/metric_type={metric_type}/{timestamp}.json"
            
            # Store in S3 Silver
            self.s3_client.put_object(
                Bucket=self.s3_bucket_silver,
                Key=s3_key,
                Body=json.dumps(aggregated_metric, indent=2),
                ContentType='application/json',
                Metadata={
                    'event-type': 'aggregated-metric',
                    'customer-id': customer_id,
                    'metric-type': metric_type,
                    'window': window,
                    'processor': 'metrics-processor'
                }
            )
            
            logger.debug(f"Stored aggregation in S3 Silver: {s3_key}")
            
        except Exception as e:
            logger.error(f"Error storing aggregation in S3 Silver: {e}")
    
    def health_check(self):
        """Periodic health check reporting"""
        while self.running:
            try:
                health_status = {
                    'processor': 'metrics-processor',
                    'status': 'healthy' if self.running else 'stopped',
                    'processed_metrics': self.processed_count,
                    'aggregations_generated': self.aggregation_count,
                    'active_customers': len(self.customer_metrics),
                    'baseline_metrics': len(self.baseline_metrics),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'window_sizes': {k: len(v) for k, v in self.metrics_windows.items()}
                }
                
                logger.info(f"Health check: {json.dumps(health_status)}")
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                time.sleep(60)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def run(self):
        """Main processing loop"""
        self.start_time = time.time()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Start background threads
        aggregation_thread = threading.Thread(target=self.generate_aggregations, daemon=True)
        aggregation_thread.start()
        
        health_thread = threading.Thread(target=self.health_check, daemon=True)
        health_thread.start()
        
        logger.info("Starting Metrics Processor...")
        
        try:
            # Setup Kafka consumer
            consumer = self.setup_consumer()
            
            # Main processing loop
            for message in consumer:
                if not self.running:
                    break
                
                try:
                    if message.value:
                        self.process_metric(message.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            logger.info(f"Shutting down. Processed {self.processed_count} metrics, generated {self.aggregation_count} aggregations")
            self.running = False

def main():
    """Main entry point"""
    processor = MetricsProcessor()
    processor.run()

if __name__ == "__main__":
    main()
