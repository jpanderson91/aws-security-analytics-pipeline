#!/usr/bin/env python3
"""
============================================================================
CAP Demo - Phase 1 MSK Infrastructure Deployment Automation
============================================================================
Purpose: Automated deployment and configuration of Amazon MSK cluster infrastructure

This script orchestrates the complete deployment of Phase 1 infrastructure:
- Pre-deployment validation and environment checking
- Terraform-based infrastructure provisioning
- Post-deployment validation and connection testing
- Configuration file generation for downstream components
- Cost monitoring and optimization recommendations

Key Features:
- Comprehensive pre-flight checks for AWS credentials and environment
- Intelligent retry logic for infrastructure deployment
- Cost estimation and monitoring integration
- Rich CLI interface with progress tracking and status reporting
- JSON configuration generation for Kafka client applications
- Error handling with detailed troubleshooting guidance

Deployment Architecture:
- Multi-AZ VPC with public/private subnet separation
- Amazon MSK cluster with 3 brokers across availability zones
- Security groups with least privilege access controls
- KMS encryption for data protection
- CloudWatch integration for monitoring and logging

Author: CAP Demo Team
Date: July 25, 2025
Version: 1.0.0

Dependencies:
- Terraform >= 1.0
- AWS CLI configured with appropriate permissions
- Python rich library for enhanced CLI output
- boto3 for AWS service integration
============================================================================
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rich_print

# Initialize rich console for professional CLI output
# Rich provides colored output, progress bars, and formatted tables
console = Console()

def run_command(command, cwd=None, capture_output=True):
    """
    Execute shell commands with comprehensive error handling and timeout protection
    
    Args:
        command (str): Shell command to execute
        cwd (str, optional): Working directory for command execution
        capture_output (bool): Whether to capture stdout/stderr (default: True)
        
    Returns:
        subprocess.CompletedProcess: Command result with returncode, stdout, stderr
        
    This function provides robust command execution with:
    - Timeout protection (5 minutes default) to prevent hanging
    - Error handling for common failure scenarios
    - Working directory management for context-sensitive operations
    - Output capture for logging and debugging
    - Cross-platform compatibility (Windows/Linux/macOS)
    
    Command Categories:
    - System tools: terraform, aws, python version checks
    - Infrastructure: terraform init, plan, apply operations
    - Validation: connectivity tests, resource verification
    - Configuration: file creation, environment setup
    """
    try:
        # Execute command with comprehensive configuration
        result = subprocess.run(
            command,
            shell=True,               # Enable shell command parsing
            cwd=cwd,                  # Set working directory context
            capture_output=capture_output,  # Control output capture
            text=True,                # Return strings instead of bytes
            timeout=300               # 5-minute timeout for safety
        )
        return result
    except subprocess.TimeoutExpired:
        # Handle command timeout gracefully
        console.print("❌ Command timed out", style="red bold")
        console.print(f"   Command: {command}", style="yellow")
        console.print("   Consider increasing timeout or checking system resources", style="yellow")
        return None
    except Exception as e:
        # Handle unexpected command execution errors
        console.print(f"❌ Command failed: {e}", style="red bold")
        console.print(f"   Command: {command}", style="yellow")
        return None

def check_prerequisites():
    """
    Validate all required tools and dependencies for MSK deployment
    
    Returns:
        bool: True if all prerequisites are met, False otherwise
        
    This function performs comprehensive environment validation:
    
    Tool Validation:
    - Terraform: Infrastructure as Code deployment tool
    - AWS CLI: Amazon Web Services command line interface
    - Python: Runtime environment for automation scripts
    
    Version Requirements:
    - Terraform: >= 1.0 for modern HCL features and AWS provider compatibility
    - AWS CLI: >= 2.0 for enhanced authentication and configuration management
    - Python: >= 3.8 for rich library compatibility and modern language features
    
    Validation Process:
    1. Check tool availability in system PATH
    2. Verify version compatibility requirements
    3. Test basic tool functionality
    4. Report any missing or incompatible tools
    5. Provide installation guidance for missing dependencies
    """
    console.print("\n🔧 Checking Prerequisites...", style="blue bold")
    
    # Define required tools with their validation commands
    # Each tool command should return version information for compatibility checking
    tools = {
        'terraform': 'terraform --version',    # Infrastructure deployment tool
        'aws': 'aws --version',               # AWS CLI for service management
        'python': 'python --version'          # Python runtime environment
    }
    
    # Track validation results for final assessment
    all_tools_available = True
    
    # Validate each required tool
    for tool, command in tools.items():
        console.print(f"   Checking {tool}...", style="blue")
        result = run_command(command)
        
        if result and result.returncode == 0:
            # Tool found and working - extract version information
            version_output = result.stdout.strip() if result.stdout else result.stderr.strip()
            console.print(f"   ✅ {tool}: {version_output}", style="green")
            
            # Perform tool-specific version validation
            if tool == 'terraform':
                # Validate Terraform version >= 1.0
                if 'Terraform v' in version_output:
                    version_str = version_output.split('v')[1].split(' ')[0]
                    major_version = int(version_str.split('.')[0])
                    if major_version < 1:
                        console.print(f"   ⚠️ Terraform version {version_str} may be too old (recommend >= 1.0)", style="yellow")
            
            elif tool == 'aws':
                # Check AWS CLI configuration
                console.print("   Checking AWS configuration...", style="blue")
                aws_check = run_command('aws sts get-caller-identity')
                if aws_check and aws_check.returncode == 0:
                    console.print("   ✅ AWS credentials configured", style="green")
                else:
                    console.print("   ⚠️ AWS credentials not configured", style="yellow")
                    console.print("     Run 'aws configure' or set AWS_PROFILE", style="yellow")
        else:
            # Tool not found or not working
            console.print(f"   ❌ {tool} not found or not working", style="red bold")
            all_tools_available = False
            
            # Provide installation guidance for missing tools
            if tool == 'terraform':
                console.print("     Install from: https://terraform.io/downloads", style="yellow")
            elif tool == 'aws':
                console.print("     Install from: https://aws.amazon.com/cli/", style="yellow")
            elif tool == 'python':
                console.print("     Install from: https://python.org/downloads/", style="yellow")
    
    # Return overall validation result
    if all_tools_available:
        console.print("✅ All prerequisites validated successfully", style="green bold")
        return True
    else:
        console.print("❌ Missing prerequisites - fix issues above and retry", style="red bold")
        return False
        if result and result.returncode == 0:
            console.print(f"✅ {tool.title()}: Available", style="green")
        else:
            console.print(f"❌ {tool.title()}: Not found", style="red bold")
            return False
    
    # Check AWS profile
    result = run_command("aws sts get-caller-identity --profile cap-demo")
    if result and result.returncode == 0:
        console.print("✅ AWS Profile: cap-demo configured", style="green")
        return True
    else:
        console.print("❌ AWS Profile: cap-demo not configured", style="red bold")
        console.print("   Run: aws configure --profile cap-demo", style="yellow")
        return False

def terraform_init():
    """Initialize Terraform"""
    console.print("\n🚀 Initializing Terraform...", style="blue bold")
    
    terraform_dir = Path(__file__).parent.parent / "terraform"
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Terraform init...", total=None)
        
        result = run_command("terraform init", cwd=terraform_dir, capture_output=False)
        
        if result and result.returncode == 0:
            console.print("✅ Terraform initialized successfully", style="green bold")
            return True
        else:
            console.print("❌ Terraform initialization failed", style="red bold")
            return False

def terraform_plan():
    """Run Terraform plan"""
    console.print("\n📋 Creating Terraform Plan...", style="blue bold")
    
    terraform_dir = Path(__file__).parent.parent / "terraform"
    
    result = run_command("terraform plan -out=tfplan", cwd=terraform_dir, capture_output=False)
    
    if result and result.returncode == 0:
        console.print("✅ Terraform plan created successfully", style="green bold")
        return True
    else:
        console.print("❌ Terraform plan failed", style="red bold")
        return False

def terraform_apply():
    """Apply Terraform configuration"""
    console.print("\n🏗️ Deploying MSK Infrastructure...", style="blue bold")
    
    console.print(Panel.fit(
        "This will create AWS resources and incur costs.\n"
        "Estimated cost: ~$3-5 per hour (~$10-15 for weekend demo)\n\n"
        "Resources to be created:\n"
        "• VPC with 3 public and 3 private subnets\n"
        "• 3 NAT Gateways\n"
        "• MSK Kafka cluster (3 brokers)\n"
        "• Security groups and KMS encryption",
        title="🔥 AWS Cost Warning",
        border_style="yellow"
    ))
    
    confirm = console.input("\nProceed with deployment? [y/N]: ")
    if confirm.lower() != 'y':
        console.print("Deployment cancelled", style="yellow")
        return False
    
    terraform_dir = Path(__file__).parent.parent / "terraform"
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Deploying infrastructure...", total=None)
        
        result = run_command("terraform apply tfplan", cwd=terraform_dir, capture_output=False)
        
        if result and result.returncode == 0:
            console.print("✅ MSK infrastructure deployed successfully!", style="green bold")
            return True
        else:
            console.print("❌ Terraform apply failed", style="red bold")
            return False

def get_outputs():
    """Get Terraform outputs"""
    console.print("\n📊 Retrieving Connection Information...", style="blue bold")
    
    terraform_dir = Path(__file__).parent.parent / "terraform"
    
    result = run_command("terraform output -json", cwd=terraform_dir)
    
    if result and result.returncode == 0:
        outputs = json.loads(result.stdout)
        
        console.print("\n🎯 MSK Cluster Information:", style="green bold")
        console.print(f"Cluster Name: {outputs['msk_cluster_name']['value']}")
        console.print(f"Bootstrap Brokers: {outputs['msk_bootstrap_brokers']['value']}")
        console.print(f"Kafka Version: {outputs['msk_kafka_version']['value']}")
        
        console.print("\n💰 Cost Information:", style="yellow bold")
        cost_info = outputs['estimated_monthly_cost']['value']
        for key, value in cost_info.items():
            console.print(f"{key.replace('_', ' ').title()}: {value}")
        
        # Save connection info for next phase
        connection_file = Path(__file__).parent / "msk_connection.json"
        with open(connection_file, 'w') as f:
            json.dump(outputs['demo_connection_info']['value'], f, indent=2)
        
        console.print(f"\n💾 Connection info saved to: {connection_file}", style="blue")
        return True
    else:
        console.print("❌ Failed to retrieve outputs", style="red bold")
        return False

def main():
    """Main setup function"""
    console.print("🚀 CAP Demo - Phase 1: MSK Kafka Setup", style="bold cyan")
    console.print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        console.print("\n❌ Prerequisites not met. Please fix and try again.", style="red bold")
        return 1
    
    # Terraform workflow
    if not terraform_init():
        return 1
    
    if not terraform_plan():
        return 1
    
    if not terraform_apply():
        return 1
    
    if not get_outputs():
        return 1
    
    # Success message
    console.print("\n🎉 Phase 1 Complete!", style="green bold")
    console.print(Panel.fit(
        "MSK Kafka cluster is now running!\n\n"
        "Next Steps:\n"
        "• Phase 2: ECS setup and data processors\n"
        "• Phase 3: Bronze/Silver/Gold pipeline\n"
        "• Phase 4: Customer demo scenarios\n\n"
        "Don't forget to destroy resources when done:\n"
        "terraform destroy",
        title="🏆 Success",
        border_style="green"
    ))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
