#!/usr/bin/env python3
"""
CAP Demo - Security Events Producer
Generates sample security events for demonstration
"""

import json
import time
import random
import argparse
from datetime import datetime, timedelta

class SecurityEventProducer:
    """
    Generates sample security events for CAP Demo
    """
    
    def __init__(self):
        self.event_types = [
            'failed_login',
            'successful_login', 
            'malware_detected',
            'network_anomaly',
            'privilege_escalation',
            'data_access',
            'system_change',
            'policy_violation'
        ]
        
        self.severity_levels = ['low', 'medium', 'high', 'critical']
        self.source_ips = [
            '192.168.1.100', '192.168.1.101', '192.168.1.102',
            '10.0.0.50', '10.0.0.51', '10.0.0.52',
            '172.16.0.10', '172.16.0.11'
        ]
        
        self.customer_ids = [
            'customer-001', 'customer-002', 'customer-003',
            'customer-004', 'customer-005'
        ]
    
    def generate_security_event(self):
        """Generate a single security event"""
        event = {
            'event_id': f"evt-{random.randint(100000, 999999)}",
            'timestamp': datetime.now().isoformat(),
            'event_type': random.choice(self.event_types),
            'severity': random.choice(self.severity_levels),
            'source_ip': random.choice(self.source_ips),
            'customer_id': random.choice(self.customer_ids),
            'user_id': f"user-{random.randint(1000, 9999)}",
            'resource': f"resource-{random.randint(100, 999)}",
            'description': f"Security event detected at {datetime.now().strftime('%H:%M:%S')}",
            'metadata': {
                'source': 'cap-demo-producer',
                'version': '1.0',
                'region': 'us-east-1'
            }
        }
        
        # Add event-specific fields
        if event['event_type'] == 'failed_login':
            event['failed_attempts'] = random.randint(1, 10)
            event['risk_score'] = random.randint(30, 90)
        elif event['event_type'] == 'malware_detected':
            event['malware_type'] = random.choice(['trojan', 'virus', 'ransomware', 'spyware'])
            event['risk_score'] = random.randint(70, 100)
        elif event['event_type'] == 'network_anomaly':
            event['bytes_transferred'] = random.randint(1000000, 10000000)
            event['risk_score'] = random.randint(40, 80)
        
        return event
    
    def generate_application_metric(self):
        """Generate application performance metric"""
        metric = {
            'metric_id': f"metric-{random.randint(100000, 999999)}",
            'timestamp': datetime.now().isoformat(),
            'customer_id': random.choice(self.customer_ids),
            'metric_type': random.choice(['cpu_usage', 'memory_usage', 'disk_io', 'network_io']),
            'value': round(random.uniform(0, 100), 2),
            'unit': random.choice(['percent', 'bytes', 'requests_per_second']),
            'service': random.choice(['web-server', 'database', 'api-gateway', 'cache']),
            'metadata': {
                'source': 'cap-demo-metrics',
                'region': 'us-east-1'
            }
        }
        
        return metric
    
    def generate_customer_event(self):
        """Generate customer lifecycle event"""
        event = {
            'event_id': f"cust-{random.randint(100000, 999999)}",
            'timestamp': datetime.now().isoformat(),
            'customer_id': random.choice(self.customer_ids),
            'event_type': random.choice(['onboarding', 'upgrade', 'support_ticket', 'billing_update']),
            'status': random.choice(['started', 'in_progress', 'completed', 'failed']),
            'metadata': {
                'source': 'cap-demo-customer',
                'region': 'us-east-1'
            }
        }
        
        return event
    
    def produce_events(self, duration_seconds=60, events_per_second=10, output_file=None):
        """Produce events for specified duration"""
        print(f"🔄 Starting event production for {duration_seconds} seconds...")
        print(f"📊 Target rate: {events_per_second} events/second")
        
        start_time = time.time()
        events_produced = 0
        
        while time.time() - start_time < duration_seconds:
            # Generate different types of events
            for _ in range(events_per_second):
                event_type = random.choice(['security', 'metric', 'customer'])
                
                if event_type == 'security':
                    event = self.generate_security_event()
                    topic = 'security-logs'
                elif event_type == 'metric':
                    event = self.generate_application_metric()
                    topic = 'app-metrics'
                else:
                    event = self.generate_customer_event()
                    topic = 'customer-events'
                
                # Output event
                event_json = json.dumps(event)
                
                if output_file:
                    output_file.write(f"{topic}: {event_json}\n")
                    output_file.flush()
                else:
                    print(f"📨 {topic}: {event['event_id' if 'event_id' in event else event['metric_id']]} ({event.get('event_type', event.get('metric_type', 'unknown'))})")
                
                events_produced += 1
            
            # Sleep to maintain rate
            time.sleep(1)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        actual_rate = events_produced / actual_duration
        
        print(f"\n✅ Event production completed!")
        print(f"📊 Total events: {events_produced}")
        print(f"⏱️ Duration: {actual_duration:.1f} seconds")
        print(f"🚀 Actual rate: {actual_rate:.1f} events/second")
        
        return events_produced

def main():
    """Main producer function"""
    parser = argparse.ArgumentParser(description='CAP Demo Security Events Producer')
    parser.add_argument('--duration', type=int, default=60,
                       help='Duration in seconds (default: 60)')
    parser.add_argument('--rate', type=int, default=10,
                       help='Events per second (default: 10)')
    parser.add_argument('--output', type=str,
                       help='Output file for events (default: stdout)')
    parser.add_argument('--test-mode', action='store_true',
                       help='Run in test mode with reduced output')
    parser.add_argument('--demo-mode', action='store_true',
                       help='Run in demo mode with enhanced output')
    
    args = parser.parse_args()
    
    # Create producer
    producer = SecurityEventProducer()
    
    # Adjust settings for different modes
    if args.test_mode:
        duration = min(args.duration, 30)  # Max 30 seconds in test mode
        rate = min(args.rate, 5)  # Max 5 events/sec in test mode
        print("🧪 Running in test mode...")
    elif args.demo_mode:
        duration = args.duration
        rate = args.rate
        print("🎬 Running in demo mode...")
    else:
        duration = args.duration
        rate = args.rate
        print("🔄 Running in normal mode...")
    
    # Open output file if specified
    output_file = None
    if args.output:
        output_file = open(args.output, 'w', encoding='utf-8')
        print(f"📁 Writing events to: {args.output}")
    
    try:
        # Produce events
        events_count = producer.produce_events(
            duration_seconds=duration,
            events_per_second=rate,
            output_file=output_file
        )
        
        print(f"\n🎉 Successfully produced {events_count} events!")
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Event production stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Event production failed: {e}")
        return 1
    finally:
        if output_file:
            output_file.close()

if __name__ == "__main__":
    exit(main())
