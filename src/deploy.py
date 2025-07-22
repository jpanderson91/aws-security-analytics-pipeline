#!/usr/bin/env python3
"""
Deployment script for Security Analytics Pipeline Lambda functions.

This script packages and deploys Lambda functions to AWS.
"""

import os
import sys
import subprocess
import zipfile
import boto3
import json
from typing import List, Dict

def create_lambda_package(function_dir: str, output_file: str) -> None:
    """Create a deployment package for a Lambda function."""
    print(f"Creating package for {function_dir}...")
    
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add Python files
        for root, dirs, files in os.walk(function_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, function_dir)
                    zipf.write(file_path, arcname)
        
        # Install dependencies if requirements.txt exists
        req_file = os.path.join(function_dir, 'requirements.txt')
        if os.path.exists(req_file):
            temp_dir = os.path.join(function_dir, 'temp_packages')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Install packages to temp directory
            subprocess.run([
                sys.executable, '-m', 'pip', 'install',
                '-r', req_file,
                '-t', temp_dir
            ], check=True)
            
            # Add packages to zip
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
            
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)
    
    print(f"Package created: {output_file}")

def update_lambda_function(function_name: str, zip_file: str) -> None:
    """Update Lambda function code."""
    lambda_client = boto3.client('lambda')
    
    with open(zip_file, 'rb') as f:
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=f.read()
        )
    
    print(f"Updated Lambda function: {function_name}")

def main():
    """Main deployment function."""
    if len(sys.argv) < 2:
        print("Usage: python deploy.py [package|deploy|all]")
        sys.exit(1)
    
    action = sys.argv[1]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Lambda functions to deploy
    functions = [
        {
            'dir': os.path.join(base_dir, 'lambda', 'event_processor'),
            'name': 'security-analytics-dev-event-processor',
            'zip': 'event_processor.zip'
        }
    ]
    
    if action in ['package', 'all']:
        print("Creating Lambda packages...")
        for func in functions:
            create_lambda_package(func['dir'], func['zip'])
    
    if action in ['deploy', 'all']:
        print("Deploying Lambda functions...")
        for func in functions:
            if os.path.exists(func['zip']):
                update_lambda_function(func['name'], func['zip'])
            else:
                print(f"Package not found: {func['zip']}. Run 'package' first.")
    
    print("Deployment complete!")

if __name__ == '__main__':
    main()
