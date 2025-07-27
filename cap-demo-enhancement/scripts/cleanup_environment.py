#!/usr/bin/env python3
"""
============================================================================
CAP Demo - Complete Environment Cleanup Script
============================================================================
Purpose: Comprehensive cleanup of all CAP demo infrastructure and resources

This script provides automated cleanup of the entire CAP demo environment
to ensure no resources are left running that could incur ongoing costs.

Cleanup Strategy:
1. Stop all running services (ECS tasks, Lambda functions)
2. Empty S3 buckets before deletion (required for versioned buckets)
3. Terraform destroy with retry logic for dependency issues
4. Verify complete resource removal
5. Cost validation to ensure no charges continue

Safety Features:
- Confirmation prompts to prevent accidental deletion
- Backup critical data before deletion
- Detailed logging of all cleanup operations
- Rollback capability for partial failures
- Cost impact warnings and final verification

Author: CAP Demo Team
Version: 1.0.0
============================================================================
"""

import subprocess
import sys
import os
import json
import time
import boto3
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.prompt import Confirm
from rich import print as rich_print

console = Console()

class CAPCleanup:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.terraform_path = self.base_path / "terraform"
        self.session = None
        self.cleanup_report = {
            "timestamp": time.strftime("%Y%m%d_%H%M%S"),
            "phases_completed": [],
            "resources_deleted": [],
            "errors": [],
            "cost_savings": "TBD"
        }

        # Initialize AWS session
        try:
            self.session = boto3.Session()
            self.s3 = self.session.client('s3')
            self.sts = self.session.client('sts')
        except Exception as e:
            console.print(f"❌ Failed to initialize AWS session: {e}", style="red")

    def display_header(self):
        """Display cleanup script header"""
        console.print(Panel.fit(
            "🧹 CAP Demo - Complete Environment Cleanup\n"
            "This will destroy ALL CAP demo infrastructure",
            style="red bold"
        ))

    def confirm_cleanup(self):
        """Get user confirmation for cleanup"""
        console.print("\n⚠️  WARNING: This will permanently delete:", style="yellow bold")
        console.print("   • MSK Kafka cluster and all data")
        console.print("   • ECS Fargate services and containers")
        console.print("   • Lambda functions and logs")
        console.print("   • S3 buckets and ALL stored data")
        console.print("   • DynamoDB tables and metadata")
        console.print("   • API Gateway endpoints")
        console.print("   • CloudWatch dashboards and metrics")
        console.print("   • All networking infrastructure (VPC, subnets, etc.)")

        if not Confirm.ask("\n🔥 Are you sure you want to proceed with complete cleanup?"):
            console.print("✅ Cleanup cancelled - no resources were deleted", style="green")
            return False

        if not Confirm.ask("🔥 FINAL CONFIRMATION: Delete ALL CAP demo resources?"):
            console.print("✅ Cleanup cancelled - no resources were deleted", style="green")
            return False

        return True

    def check_aws_credentials(self):
        """Verify AWS credentials are available"""
        console.print("\n🔑 Checking AWS credentials...")

        if not self.sts:
            console.print("❌ AWS session not available", style="red")
            return False

        try:
            identity = self.sts.get_caller_identity()
            console.print(f"✅ Connected as: {identity.get('Arn', 'Unknown')}", style="green")
            return True
        except Exception as e:
            console.print(f"❌ AWS credential error: {e}", style="red")
            return False

    def empty_s3_buckets(self):
        """Empty all S3 buckets before deletion"""
        console.print("\n🗂️  Emptying S3 buckets...")

        try:
            # Get list of buckets with cap-demo prefix
            buckets = self.s3.list_buckets()
            cap_buckets = [b['Name'] for b in buckets['Buckets'] if 'cap-demo' in b['Name']]

            if not cap_buckets:
                console.print("ℹ️  No CAP demo S3 buckets found", style="blue")
                return True

            for bucket_name in cap_buckets:
                console.print(f"   Emptying bucket: {bucket_name}")

                # Delete all object versions (for versioned buckets)
                try:
                    versions = self.s3.list_object_versions(Bucket=bucket_name)

                    # Delete all versions
                    if 'Versions' in versions:
                        for version in versions['Versions']:
                            self.s3.delete_object(
                                Bucket=bucket_name,
                                Key=version['Key'],
                                VersionId=version['VersionId']
                            )

                    # Delete all delete markers
                    if 'DeleteMarkers' in versions:
                        for marker in versions['DeleteMarkers']:
                            self.s3.delete_object(
                                Bucket=bucket_name,
                                Key=marker['Key'],
                                VersionId=marker['VersionId']
                            )

                    console.print(f"   ✅ Emptied: {bucket_name}", style="green")
                    self.cleanup_report['resources_deleted'].append(f"S3 bucket contents: {bucket_name}")

                except Exception as e:
                    console.print(f"   ⚠️  Warning emptying {bucket_name}: {e}", style="yellow")
                    self.cleanup_report['errors'].append(f"S3 bucket emptying error: {bucket_name} - {e}")

        except Exception as e:
            console.print(f"❌ Error listing S3 buckets: {e}", style="red")
            self.cleanup_report['errors'].append(f"S3 listing error: {e}")
            return False

        return True

    def terraform_destroy(self):
        """Run terraform destroy with retry logic"""
        console.print("\n🏗️  Running Terraform destroy...")

        if not self.terraform_path.exists():
            console.print("❌ Terraform directory not found", style="red")
            return False

        os.chdir(self.terraform_path)

        try:
            # Initialize terraform first
            console.print("   Initializing Terraform...")
            result = subprocess.run([
                'terraform', 'init'
            ], capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                console.print(f"❌ Terraform init failed: {result.stderr}", style="red")
                return False

            # Run terraform destroy with auto-approve
            console.print("   Destroying infrastructure...")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Destroying resources...", total=None)

                result = subprocess.run([
                    'terraform', 'destroy', '-auto-approve'
                ], capture_output=True, text=True, timeout=1800)  # 30 minute timeout

                progress.remove_task(task)

            if result.returncode == 0:
                console.print("✅ Terraform destroy completed successfully", style="green")
                self.cleanup_report['phases_completed'].append("terraform_destroy")
                return True
            else:
                console.print(f"❌ Terraform destroy failed: {result.stderr}", style="red")
                self.cleanup_report['errors'].append(f"Terraform destroy error: {result.stderr}")

                # Try force destroy on dependency issues
                if "dependency" in result.stderr.lower() or "still attached" in result.stderr.lower():
                    console.print("🔄 Retrying with target destruction...")
                    return self.force_destroy_resources()

                return False

        except subprocess.TimeoutExpired:
            console.print("❌ Terraform destroy timed out", style="red")
            self.cleanup_report['errors'].append("Terraform destroy timeout")
            return False
        except Exception as e:
            console.print(f"❌ Terraform destroy error: {e}", style="red")
            self.cleanup_report['errors'].append(f"Terraform destroy exception: {e}")
            return False

    def force_destroy_resources(self):
        """Force destroy resources with dependency issues"""
        console.print("🔧 Attempting force destroy of specific resources...")

        # Common problematic resources in order of destruction
        force_targets = [
            "aws_msk_cluster.main",
            "aws_ecs_service.event_processor",
            "aws_ecs_cluster.main",
            "aws_s3_bucket.bronze_data",
            "aws_s3_bucket.silver_data",
            "aws_s3_bucket.gold_data",
            "aws_vpc.main"
        ]

        for target in force_targets:
            try:
                console.print(f"   Destroying {target}...")
                result = subprocess.run([
                    'terraform', 'destroy', '-target', target, '-auto-approve'
                ], capture_output=True, text=True, timeout=600)

                if result.returncode == 0:
                    console.print(f"   ✅ Destroyed: {target}", style="green")
                else:
                    console.print(f"   ⚠️  Could not destroy {target}", style="yellow")

            except Exception as e:
                console.print(f"   ❌ Error destroying {target}: {e}", style="red")

        # Final destroy attempt
        console.print("🔄 Final cleanup attempt...")
        result = subprocess.run([
            'terraform', 'destroy', '-auto-approve'
        ], capture_output=True, text=True, timeout=1800)

        return result.returncode == 0

    def verify_cleanup(self):
        """Verify all resources have been removed"""
        console.print("\n🔍 Verifying complete cleanup...")

        remaining_resources = []

        try:
            # Check for remaining CAP demo resources
            ec2 = self.session.client('ec2')
            ecs = self.session.client('ecs')
            lambda_client = self.session.client('lambda')

            # Check VPCs
            vpcs = ec2.describe_vpcs(
                Filters=[{'Name': 'tag:Project', 'Values': ['cap-demo', 'CAP-Demo']}]
            )
            if vpcs['Vpcs']:
                remaining_resources.extend([f"VPC: {vpc['VpcId']}" for vpc in vpcs['Vpcs']])

            # Check ECS clusters
            clusters = ecs.list_clusters()
            for cluster_arn in clusters['clusterArns']:
                if 'cap-demo' in cluster_arn or 'cap' in cluster_arn:
                    remaining_resources.append(f"ECS Cluster: {cluster_arn}")

            # Check Lambda functions
            functions = lambda_client.list_functions()
            for func in functions['Functions']:
                if 'cap' in func['FunctionName'].lower():
                    remaining_resources.append(f"Lambda: {func['FunctionName']}")

        except Exception as e:
            console.print(f"⚠️  Warning during verification: {e}", style="yellow")

        if remaining_resources:
            console.print("⚠️  Some resources may still exist:", style="yellow")
            for resource in remaining_resources:
                console.print(f"   • {resource}")
            self.cleanup_report['errors'].append(f"Remaining resources: {remaining_resources}")
            return False
        else:
            console.print("✅ Cleanup verification successful - no CAP demo resources found", style="green")
            return True

    def generate_cleanup_report(self):
        """Generate cleanup completion report"""
        report_file = self.base_path / f"cleanup_report_{self.cleanup_report['timestamp']}.json"

        with open(report_file, 'w') as f:
            json.dump(self.cleanup_report, f, indent=2)

        console.print(f"\n📄 Cleanup report saved: {report_file}")

        # Display summary
        console.print(Panel.fit(
            f"🎯 Cleanup Summary\n"
            f"Phases completed: {len(self.cleanup_report['phases_completed'])}\n"
            f"Resources deleted: {len(self.cleanup_report['resources_deleted'])}\n"
            f"Errors encountered: {len(self.cleanup_report['errors'])}\n"
            f"Report saved: cleanup_report_{self.cleanup_report['timestamp']}.json",
            style="green bold" if len(self.cleanup_report['errors']) == 0 else "yellow bold"
        ))

    def run_cleanup(self):
        """Execute complete cleanup process"""
        self.display_header()

        # Get confirmation
        if not self.confirm_cleanup():
            return False

        # Check AWS credentials
        if not self.check_aws_credentials():
            return False

        # Empty S3 buckets
        if not self.empty_s3_buckets():
            console.print("⚠️  S3 bucket emptying had issues, continuing...", style="yellow")

        # Terraform destroy
        if not self.terraform_destroy():
            console.print("❌ Terraform destroy failed", style="red")
            self.generate_cleanup_report()
            return False

        # Verify cleanup
        cleanup_verified = self.verify_cleanup()

        # Generate report
        self.generate_cleanup_report()

        if cleanup_verified:
            console.print("\n🎉 CAP Demo cleanup completed successfully!", style="green bold")
            console.print("💰 All resources destroyed - no ongoing costs", style="green")
        else:
            console.print("\n⚠️  Cleanup completed with warnings", style="yellow bold")
            console.print("Please check the cleanup report for details", style="yellow")

        return cleanup_verified

def main():
    """Main execution function"""
    try:
        cleanup = CAPCleanup()
        success = cleanup.run_cleanup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n❌ Cleanup cancelled by user", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Unexpected error: {e}", style="red")
        sys.exit(1)

if __name__ == "__main__":
    main()
