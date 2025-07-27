#!/usr/bin/env python3
"""
CAP Demo Environment Test Script
Tests AWS connectivity and required dependencies for the CAP Data Ingestion Platform Demo
"""

import sys
import subprocess
import boto3
from rich.console import Console
from rich.table import Table
from rich import print

console = Console()

def test_aws_connection():
    """Test AWS connectivity using current profile"""
    try:
        session = boto3.Session(profile_name='cap-demo') # <--- ADD THIS LINE
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        
        console.print("✅ AWS Connection:", style="green bold")
        console.print(f"   Account: {identity['Account']}")
        console.print(f"   User: {identity['Arn'].split('/')[-1]}")
        console.print(f"   Region: {session.region_name or 'us-east-1'}")
        return True
    except Exception as e:
        console.print(f"❌ AWS connection failed: {e}", style="red bold")
        return False

def test_python_environment():
    """Test Python environment and required packages"""
    console.print("\n🐍 Python Environment:", style="blue bold")
    console.print(f"   Version: {sys.version.split()[0]}")
    
    required_modules = [
        'boto3', 'kafka', 'pandas', 'docker', 
        'sqlalchemy', 'pydantic', 'pytest'
    ]
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Module", style="dim")
    table.add_column("Status", justify="center")
    table.add_column("Version", style="dim")
    
    all_good = True
    for module in required_modules:
        try:
            imported = __import__(module)
            version = getattr(imported, '__version__', 'Unknown')
            table.add_row(module, "✅", version)
        except ImportError:
            table.add_row(module, "❌", "Not installed")
            all_good = False
    
    console.print(table)
    return all_good

def test_tools():
    """Test required command-line tools"""
    console.print("\n🛠️ Command Line Tools:", style="blue bold")
    
    tools = [
        ('terraform', '--version'),
        ('docker', '--version'),
        ('aws', '--version')
    ]
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Tool", style="dim")
    table.add_column("Status", justify="center")
    table.add_column("Version", style="dim")
    
    all_good = True
    for tool, version_flag in tools:
        try:
            result = subprocess.run(
                [tool, version_flag], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                # Extract version from output
                version = result.stdout.split('\n')[0]
                table.add_row(tool, "✅", version[:50])
            else:
                table.add_row(tool, "❌", "Failed to get version")
                all_good = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            table.add_row(tool, "❌", "Not found")
            all_good = False
    
    console.print(table)
    return all_good

def main():
    """Run all environment tests"""
    console.print("🔧 CAP Demo Environment Test", style="bold yellow")
    console.print("=" * 50)
    
    aws_ok = test_aws_connection()
    python_ok = test_python_environment()
    tools_ok = test_tools()
    
    console.print("\n📊 Summary:", style="bold yellow")
    if aws_ok and python_ok and tools_ok:
        console.print("✅ Environment is ready for CAP demo development!", style="green bold")
        return 0
    else:
        console.print("❌ Environment needs fixes before proceeding", style="red bold")
        console.print("\nNext steps:")
        if not python_ok:
            console.print("   • Install missing Python packages: pip install -r cap-requirements.txt")
        if not tools_ok:
            console.print("   • Install missing command-line tools")
        if not aws_ok:
            console.print("   • Configure AWS credentials: aws configure")
        return 1

if __name__ == "__main__":
    sys.exit(main())
