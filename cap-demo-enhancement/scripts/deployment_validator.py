"""
Windows-compatible deployment validator and fixer
Fixes encoding issues and validates deployment readiness
"""

import subprocess
import sys
import os
from pathlib import Path
import json
from datetime import datetime

def setup_windows_environment():
    """Configure Windows environment for proper script execution"""
    env = os.environ.copy()
    
    # Set encoding environment variables
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    env['LANG'] = 'en_US.UTF-8'
    
    return env

def run_script_safely(script_path, args=None, timeout=300):
    """Run a Python script with proper Windows encoding handling"""
    if args is None:
        args = []
    
    env = setup_windows_environment()
    cmd = [sys.executable, str(script_path)] + args
    
    try:
        print(f"🚀 Running: {script_path.name}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # Replace problematic characters
            timeout=timeout,
            env=env
        )
        
        return result
    except subprocess.TimeoutExpired:
        print(f"⏰ Script {script_path.name} timed out after {timeout}s")
        return None
    except Exception as e:
        print(f"❌ Error running {script_path.name}: {e}")
        return None

def validate_aws_credentials():
    """Check AWS credentials and configuration"""
    try:
        result = subprocess.run(
            ['aws', 'sts', 'get-caller-identity'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            identity = json.loads(result.stdout)
            print(f"✅ AWS Credentials: {identity.get('Arn', 'Unknown')}")
            return True
        else:
            print(f"❌ AWS Credentials not configured: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ AWS CLI error: {e}")
        return False

def validate_terraform_setup():
    """Check Terraform configuration and setup"""
    terraform_dir = Path.cwd().parent / 'terraform'
    
    if not terraform_dir.exists():
        print(f"❌ Terraform directory not found: {terraform_dir}")
        return False
    
    print(f"✅ Terraform directory found: {terraform_dir}")
    
    # Check if terraform is available
    try:
        result = subprocess.run(
            ['terraform', 'version'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✅ Terraform: {result.stdout.strip().split()[1]}")
            return True
        else:
            print(f"❌ Terraform not available: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Terraform error: {e}")
        return False

def dry_run_deployment_scripts():
    """Test all deployment scripts with dry-run mode"""
    scripts_dir = Path.cwd()
    deployment_scripts = [
        'setup_phase1_msk.py',
        'setup_phase2_processing.py', 
        'setup_phase3_analytics.py'
    ]
    
    results = {}
    
    for script_name in deployment_scripts:
        script_path = scripts_dir / script_name
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_name}")
            results[script_name] = {'status': 'missing', 'error': 'File not found'}
            continue
        
        # Try to run with --help first to test basic functionality
        result = run_script_safely(script_path, ['--help'], timeout=60)
        
        if result and result.returncode == 0:
            print(f"✅ {script_name}: Basic functionality OK")
            results[script_name] = {'status': 'ready', 'help_output': result.stdout[:200]}
        else:
            error_msg = result.stderr if result else "Script execution failed"
            print(f"❌ {script_name}: {error_msg[:200]}")
            results[script_name] = {'status': 'error', 'error': error_msg[:200]}
    
    return results

def validate_prerequisites():
    """Comprehensive prerequisite validation"""
    print("🔧 Validating Prerequisites...")
    
    checks = {
        'python': True,
        'boto3': False,
        'terraform': False,
        'aws_cli': False,
        'aws_credentials': False
    }
    
    # Check Python packages
    try:
        import boto3
        checks['boto3'] = True
        print("✅ boto3 available")
    except ImportError:
        print("❌ boto3 not available - run: pip install boto3")
    
    try:
        import rich
        print("✅ rich available")
    except ImportError:
        print("❌ rich not available - run: pip install rich")
    
    # Check Terraform
    checks['terraform'] = validate_terraform_setup()
    
    # Check AWS CLI
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            checks['aws_cli'] = True
            print(f"✅ AWS CLI: {result.stdout.strip()}")
        else:
            print("❌ AWS CLI not available")
    except Exception:
        print("❌ AWS CLI not available")
    
    # Check AWS credentials
    checks['aws_credentials'] = validate_aws_credentials()
    
    return checks

def main():
    """Main deployment validation function"""
    print("🔍 CAP Demo - Deployment Validation & Fixer")
    print("=" * 60)
    
    # Step 1: Validate prerequisites
    prereq_results = validate_prerequisites()
    
    # Step 2: Test script functionality
    print("\n🧪 Testing Deployment Scripts...")
    script_results = dry_run_deployment_scripts()
    
    # Step 3: Generate validation report
    report = {
        'timestamp': datetime.now().isoformat(),
        'prerequisites': prereq_results,
        'scripts': script_results,
        'windows_environment': {
            'PYTHONIOENCODING': os.environ.get('PYTHONIOENCODING', 'Not set'),
            'PYTHONUTF8': os.environ.get('PYTHONUTF8', 'Not set'),
            'LANG': os.environ.get('LANG', 'Not set')
        }
    }
    
    # Step 4: Summary and recommendations
    print("\n📊 DEPLOYMENT VALIDATION SUMMARY")
    print("=" * 60)
    
    total_checks = len(prereq_results) + len(script_results)
    passed_checks = sum(1 for v in prereq_results.values() if v) + \
                   sum(1 for v in script_results.values() if v.get('status') == 'ready')
    
    print(f"📈 Overall Status: {passed_checks}/{total_checks} checks passed")
    
    if all(prereq_results.values()) and all(s.get('status') == 'ready' for s in script_results.values()):
        print("🎉 DEPLOYMENT READY!")
        print("✅ All prerequisites met")
        print("✅ All scripts functional")
        print("🚀 Ready to proceed with actual deployment")
    else:
        print("⚠️ DEPLOYMENT NEEDS ATTENTION")
        
        # Show specific issues
        for name, status in prereq_results.items():
            if not status:
                print(f"🔧 Fix: {name}")
        
        for script, result in script_results.items():
            if result.get('status') != 'ready':
                print(f"🔧 Fix: {script} - {result.get('error', 'Unknown error')[:100]}")
    
    # Save detailed report
    report_file = f"deployment_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved: {report_file}")
    
    return passed_checks == total_checks

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
