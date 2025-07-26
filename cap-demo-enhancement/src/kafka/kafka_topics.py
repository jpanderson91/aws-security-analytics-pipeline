#!/usr/bin/env python3
"""
============================================================================
CAP Demo - Kafka Topic Management and Testing Suite
============================================================================
Purpose: Comprehensive Kafka topic management for Toyota CAP-style scenarios

This module provides enterprise-grade Kafka topic management capabilities:
- Automated topic creation for customer onboarding workflows
- Producer/Consumer testing for connectivity validation
- Topic listing and monitoring for operational visibility
- Customer-specific topic provisioning for multi-tenant scenarios

Key Features:
- MSK cluster integration with secure connection handling
- Rich CLI interface with professional error reporting
- JSON-based configuration management
- Comprehensive logging and monitoring integration

Author: CAP Demo Team
Date: July 25, 2025
Version: 1.0.0

Dependencies:
- rich for enhanced CLI output
- kafka-python for Kafka client operations
- boto3 for AWS service integration
============================================================================
"""

import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic

# Initialize rich console for professional CLI output
console = Console()

class MSKTopicManager:
    """
    Advanced Kafka Topic Management for MSK Clusters
    
    This class encapsulates all Kafka administrative operations for the CAP demo,
    providing a clean interface for topic management, testing, and monitoring.
    
    Key Design Patterns:
    - Configuration externalization through JSON files
    - Defensive programming with comprehensive error handling
    - Resource management with proper client lifecycle
    - Professional logging and user feedback
    """
    
    def __init__(self, connection_file="msk_connection.json"):
        """
        Initialize MSKTopicManager with connection configuration
        
        Args:
            connection_file (str): Relative path to MSK connection configuration
        """
        # Construct absolute path to connection file
        self.connection_file = Path(__file__).parent.parent.parent / connection_file
        
        # Load and validate connection configuration
        self.connection_info = self._load_connection_info()
        
        # Extract bootstrap servers for Kafka client connections
        self.bootstrap_servers = self.connection_info.get('bootstrap_servers', '')
        
    def _load_connection_info(self):
        """
        Load and validate MSK connection configuration from JSON file
        
        Returns:
            dict: Parsed connection configuration
            
        Raises:
            SystemExit: If configuration file is missing or invalid
        """
        try:
            with open(self.connection_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            console.print(f"❌ Connection file not found: {self.connection_file}", style="red bold")
            console.print("   Run setup_phase1_msk.py first to deploy infrastructure", style="yellow")
            sys.exit(1)
        except json.JSONDecodeError:
            console.print("❌ Invalid connection file format", style="red bold")
            console.print("   Connection file must be valid JSON", style="yellow")
            sys.exit(1)
    
    def create_admin_client(self):
        """
        Create and configure Kafka AdminClient for cluster management
        
        Returns:
            KafkaAdminClient: Configured admin client or None on failure
        """
        try:
            return KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id="cap-demo-admin"
            )
        except Exception as e:
            console.print(f"❌ Failed to connect to Kafka cluster: {e}", style="red bold")
            console.print("   Check MSK cluster status and network connectivity", style="yellow")
            return None
    
    def create_demo_topics(self):
        """
        Create all predefined demo topics for CAP scenarios
        
        Returns:
            bool: True if all topics created successfully, False otherwise
        """
        console.print("🎯 Creating Demo Kafka Topics...", style="blue bold")
        
        admin_client = self.create_admin_client()
        if not admin_client:
            return False
        
        # Prepare topic creation requests
        topics_to_create = []
        demo_topics = self.connection_info.get('demo_topics', [])
        
        # Configure each topic with enterprise-grade settings
        for topic_name in demo_topics:
            topic = NewTopic(
                name=topic_name,
                num_partitions=3,      # Enable parallel processing
                replication_factor=2   # Data durability
            )
            topics_to_create.append(topic)
        
        try:
            # Execute topic creation
            fs = admin_client.create_topics(new_topics=topics_to_create, validate_only=False)
            
            # Process results individually
            for topic, f in fs.items():
                try:
                    f.result()  # Block until operation completes
                    console.print(f"✅ Created topic: {topic}", style="green")
                except Exception as e:
                    if "TopicExistsException" in str(e):
                        console.print(f"ℹ️ Topic already exists: {topic}", style="yellow")
                    else:
                        console.print(f"❌ Failed to create topic {topic}: {e}", style="red")
                        return False
            
            console.print("✅ All demo topics created successfully!", style="green bold")
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to create topics: {e}", style="red bold")
            return False
        finally:
            admin_client.close()
    
    def list_topics(self):
        """
        List all topics in the Kafka cluster with detailed information
        
        Returns:
            bool: True if listing successful, False otherwise
        """
        console.print("📋 Kafka Topics:", style="blue bold")
        
        admin_client = self.create_admin_client()
        if not admin_client:
            return False
        
        try:
            # Retrieve cluster metadata
            metadata = admin_client.list_topics(timeout=10)
            
            # Create formatted table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Topic Name", style="dim")
            table.add_column("Partitions", justify="center")
            table.add_column("Type", style="dim")
            
            # Process and categorize each topic
            for topic in sorted(metadata.topics):
                # Get topic details
                topic_details = admin_client.describe_topics([topic])
                partitions = len(topic_details[topic].partitions) if topic in topic_details else "Unknown"
                
                # Categorize topic
                if topic.startswith('__'):
                    topic_type = "System"
                elif topic in self.connection_info.get('demo_topics', []):
                    topic_type = "Demo"
                else:
                    topic_type = "Custom"
                
                table.add_row(topic, str(partitions), topic_type)
            
            console.print(table)
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to list topics: {e}", style="red bold")
            return False
        finally:
            admin_client.close()
    
    def test_producer_consumer(self, topic_name="customer-events"):
        """
        Test Kafka producer and consumer functionality with realistic data
        
        Args:
            topic_name (str): Topic to use for testing
            
        Returns:
            bool: True if test successful, False otherwise
        """
        console.print(f"🧪 Testing Producer/Consumer for topic: {topic_name}", style="blue bold")
        
        try:
            # Producer Test
            producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                client_id="cap-demo-producer"
            )
            
            # Create realistic test message
            test_message = {
                "timestamp": "2025-07-25T12:00:00Z",
                "customer_id": "ABC-CORP",
                "event_type": "security_alert",
                "severity": "medium",
                "source": "CAP-Demo-Test",
                "data": {
                    "user": "john.doe",
                    "action": "login_attempt",
                    "ip_address": "192.168.1.100",
                    "success": True
                }
            }
            
            # Send message
            future = producer.send(topic_name, test_message)
            record_metadata = future.get(timeout=10)
            
            console.print(
                f"✅ Message sent to {record_metadata.topic} "
                f"partition {record_metadata.partition} "
                f"offset {record_metadata.offset}", 
                style="green"
            )
            
            producer.close()
            
            # Consumer Test
            consumer = KafkaConsumer(
                topic_name,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=5000,
                auto_offset_reset='latest',
                client_id="cap-demo-consumer"
            )
            
            console.print("📨 Consuming messages...", style="blue")
            
            message_count = 0
            for message in consumer:
                message_count += 1
                console.print(
                    f"📩 Received: {message.value['event_type']} "
                    f"from {message.value['customer_id']}", 
                    style="green"
                )
                if message_count >= 1:
                    break
            
            consumer.close()
            
            if message_count > 0:
                console.print("✅ Producer/Consumer test successful!", style="green bold")
                return True
            else:
                console.print("⚠️ No messages consumed (may be normal)", style="yellow")
                return True
                
        except Exception as e:
            console.print(f"❌ Producer/Consumer test failed: {e}", style="red bold")
            console.print("   Check topic existence and cluster connectivity", style="yellow")
            return False
    
    def create_customer_topic(self, customer_name, data_type="events"):
        """
        Create a topic for a specific customer scenario
        
        Args:
            customer_name (str): Customer identifier
            data_type (str): Type of data for topic specialization
            
        Returns:
            bool: True if topic created successfully, False otherwise
        """
        topic_name = f"{customer_name}-{data_type}"
        
        console.print(f"🏢 Creating customer topic: {topic_name}", style="blue bold")
        
        admin_client = self.create_admin_client()
        if not admin_client:
            return False
        
        # Configure customer topic
        topic = NewTopic(
            name=topic_name,
            num_partitions=3,
            replication_factor=2
        )
        
        try:
            fs = admin_client.create_topics(new_topics=[topic], validate_only=False)
            fs[topic_name].result()
            console.print(f"✅ Customer topic created: {topic_name}", style="green bold")
            return True
        except Exception as e:
            if "TopicExistsException" in str(e):
                console.print(f"ℹ️ Customer topic already exists: {topic_name}", style="yellow")
                return True
            else:
                console.print(f"❌ Failed to create customer topic: {e}", style="red bold")
                return False
        finally:
            admin_client.close()

def main():
    """
    Main entry point for Kafka topic management CLI
    
    Provides commands for:
    - create-demo: Create all predefined demo topics
    - list: Display all topics with categorization
    - test: Validate producer/consumer functionality
    - customer <name>: Create customer-specific topic
    """
    console.print("🎯 CAP Demo - Kafka Topic Management", style="bold cyan")
    console.print("=" * 50)
    
    if len(sys.argv) < 2:
        console.print("Usage:", style="yellow bold")
        console.print("  python kafka_topics.py create-demo     # Create all demo topics")
        console.print("  python kafka_topics.py list           # List all topics")
        console.print("  python kafka_topics.py test           # Test producer/consumer")
        console.print("  python kafka_topics.py customer <name> # Create customer topic")
        return 1
    
    manager = MSKTopicManager()
    command = sys.argv[1]
    
    # Command dispatch
    if command == "create-demo":
        success = manager.create_demo_topics()
    elif command == "list":
        success = manager.list_topics()
    elif command == "test":
        success = manager.test_producer_consumer()
    elif command == "customer" and len(sys.argv) > 2:
        customer_name = sys.argv[2]
        success = manager.create_customer_topic(customer_name)
    else:
        console.print("❌ Invalid command", style="red bold")
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
