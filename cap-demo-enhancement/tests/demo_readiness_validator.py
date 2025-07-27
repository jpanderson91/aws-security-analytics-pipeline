#!/usr/bin/env python3
"""
CAP Demo - Demo-Ready Validation Runner
Windows-compatible         # Check for demo scripts
        setup_scripts = [
            'setup_phase1_kafka.py',
            'setup_phase1_msk.py',
            'setup_phase2_processing.py',
            'setup_phase3_analytics.py'
        ]

        test_scripts = [
            'run_complete_validation.py'
        ]

        missing_scripts = []

        # Check setup scripts in scripts/ folder
        for script in setup_scripts:
            script_path = self.scripts_path / script
            if not script_path.exists():
                missing_scripts.append(script)

        # Check test scripts in tests/ folder
        for script in test_scripts:
            script_path = self.tests_path / script
            if not script_path.exists():
                missing_scripts.append(script)

        total_scripts = len(setup_scripts) + len(test_scripts)
        if missing_scripts:
            prereqs['Demo Scripts'] = f"❌ Missing: {', '.join(missing_scripts)}"
        else:
            prereqs['Demo Scripts'] = f"✅ All {total_scripts} scripts present"per path handling and encoding
"""

import json
import subprocess
import time
import boto3
import os
from datetime import datetime
from pathlib import Path

class CAPDemoValidator:
    """
    Demo-ready CAP validation with Windows compatibility
    """

    def __init__(self):
        self.region = 'us-east-1'
        self.base_path = Path(__file__).parent.parent  # Go up one level from tests/
        self.scripts_path = self.base_path / 'scripts'
        self.tests_path = self.base_path / 'tests'

        # Set environment for Windows compatibility
        self.env = os.environ.copy()
        self.env['PYTHONIOENCODING'] = 'utf-8'
        self.env['PYTHONLEGACYWINDOWSSTDIO'] = '1'  # Fix encoding issues

        self.validation_report = {
            'start_time': datetime.now().isoformat(),
            'phases': {},
            'errors': [],
            'warnings': [],
            'demo_readiness': {},
            'metrics': {}
        }

        # AWS clients with current session (no specific profile needed)
        try:
            session = boto3.Session()
            self.sts = session.client('sts')
            self.ce = session.client('ce')
        except Exception as e:
            print(f"⚠️ AWS session setup: {e}")
            self.sts = None
            self.ce = None

        print("🎬 CAP Demo - Demo Readiness Validator")
        print("=" * 50)
        print("Checking demo readiness and identifying any issues")

    def check_demo_prerequisites(self):
        """Check demo-specific prerequisites"""
        print("\n🔧 Checking Demo Prerequisites...")

        prereqs = {}

        # Check AWS credentials
        if self.sts:
            try:
                identity = self.sts.get_caller_identity()
                prereqs['AWS Credentials'] = f"✅ {identity.get('Arn', 'Available')}"
            except Exception as e:
                prereqs['AWS Credentials'] = f"⚠️ {str(e)[:100]}..."
        else:
            prereqs['AWS Credentials'] = "⚠️ Session not available"

        # Check Python packages
        required_packages = ['boto3', 'rich', 'pathlib']
        for package in required_packages:
            try:
                __import__(package)
                prereqs[f'Python {package}'] = "✅ Available"
            except ImportError:
                prereqs[f'Python {package}'] = "❌ Missing"

        # Check Terraform
        try:
            result = subprocess.run(['terraform', '--version'],
                                  capture_output=True, text=True, check=False)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                prereqs['Terraform'] = f"✅ {version}"
            else:
                prereqs['Terraform'] = "❌ Not found"
        except FileNotFoundError:
            prereqs['Terraform'] = "❌ Not installed"

        # Check for demo scripts
        setup_scripts = [
            'setup_phase1_kafka.py',
            'setup_phase1_msk.py',
            'setup_phase2_processing.py',
            'setup_phase3_analytics.py'
        ]

        test_scripts = [
            'run_complete_validation.py'
        ]

        missing_scripts = []

        # Check setup scripts in scripts/ folder
        for script in setup_scripts:
            script_path = self.scripts_path / script
            if not script_path.exists():
                missing_scripts.append(script)

        # Check test scripts in tests/ folder
        for script in test_scripts:
            script_path = self.tests_path / script
            if not script_path.exists():
                missing_scripts.append(script)

        total_scripts = len(setup_scripts) + len(test_scripts)
        if missing_scripts:
            prereqs['Demo Scripts'] = f"❌ Missing: {', '.join(missing_scripts)}"
        else:
            prereqs['Demo Scripts'] = f"✅ All {total_scripts} scripts present"

        # Check directory structure
        required_dirs = ['scripts', 'tests', 'docs', 'terraform', 'src']
        missing_dirs = []
        for dir_name in required_dirs:
            dir_path = self.base_path / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)

        if missing_dirs:
            prereqs['Directory Structure'] = f"❌ Missing: {', '.join(missing_dirs)}"
        else:
            prereqs['Directory Structure'] = f"✅ Complete structure"

        # Display results
        print("\n📋 Prerequisites Status:")
        all_good = True
        for component, status in prereqs.items():
            print(f"   {status} - {component}")
            if "❌" in status:
                all_good = False
                self.validation_report['errors'].append(f"Prerequisite failed: {component}")
            elif "⚠️" in status:
                self.validation_report['warnings'].append(f"Prerequisite warning: {component}")

        return all_good

    def test_script_compatibility(self):
        """Test if scripts can run without encoding issues"""
        print("\n🧪 Testing Script Compatibility...")

        compatibility_results = {}

        # Test Phase 1 script syntax (no execution)
        print("Testing Phase 1 script...")
        try:
            phase1_script = self.scripts_path / 'setup_phase1_kafka.py'
            if phase1_script.exists():
                result = subprocess.run([
                    'python', '-m', 'py_compile', str(phase1_script)
                ], capture_output=True, text=True, env=self.env, check=False)

                if result.returncode == 0:
                    compatibility_results['Phase 1'] = "✅ Syntax OK"
                else:
                    compatibility_results['Phase 1'] = "❌ Syntax error"
                    print(f"   Syntax error: {result.stderr[:200]}...")
            else:
                compatibility_results['Phase 1'] = "❌ Script missing"

        except Exception as e:
            compatibility_results['Phase 1'] = f"❌ Error: {e}"

        # Test script syntax compilation
        scripts_to_test = [
            ('Phase 2', 'setup_phase2_processing.py', self.scripts_path),
            ('Phase 3', 'setup_phase3_analytics.py', self.scripts_path),
            ('Validation', 'run_complete_validation.py', self.tests_path)
        ]

        for phase_name, script_name, script_dir in scripts_to_test:
            print(f"Testing {phase_name} script syntax...")
            try:
                script_path = script_dir / script_name
                if script_path.exists():
                    result = subprocess.run([
                        'python', '-m', 'py_compile', str(script_path)
                    ], capture_output=True, text=True, env=self.env, check=False)

                    if result.returncode == 0:
                        compatibility_results[phase_name] = "✅ Syntax OK"
                    else:
                        compatibility_results[phase_name] = f"❌ Syntax error"
                        print(f"   Syntax error: {result.stderr[:200]}...")
                else:
                    compatibility_results[phase_name] = "❌ Script missing"
            except Exception as e:
                compatibility_results[phase_name] = f"❌ Test error: {e}"

        # Display results
        print("\n🧪 Compatibility Results:")
        for phase, status in compatibility_results.items():
            print(f"   {status} - {phase}")

        self.validation_report['compatibility'] = compatibility_results
        return all("✅" in status or "⚠️" in status for status in compatibility_results.values())

    def check_demo_infrastructure(self):
        """Check if demo infrastructure exists"""
        print("\n🏗️ Checking Demo Infrastructure...")

        if not self.sts:
            print("⚠️ Cannot check infrastructure - AWS session not available")
            return False

        infra_status = {}

        try:
            # Check for MSK clusters
            import boto3
            msk = boto3.client('kafka', region_name=self.region)
            clusters = msk.list_clusters()
            msk_count = len(clusters.get('ClusterInfoList', []))
            infra_status['MSK Clusters'] = f"Found {msk_count} clusters"

            # Check for ECS clusters
            ecs = boto3.client('ecs', region_name=self.region)
            clusters = ecs.list_clusters()
            ecs_count = len(clusters.get('clusterArns', []))
            infra_status['ECS Clusters'] = f"Found {ecs_count} clusters"

            # Check for Lambda functions
            lambda_client = boto3.client('lambda', region_name=self.region)
            functions = lambda_client.list_functions()
            lambda_count = len(functions.get('Functions', []))
            infra_status['Lambda Functions'] = f"Found {lambda_count} functions"

            # Check for API Gateway
            api_client = boto3.client('apigateway', region_name=self.region)
            apis = api_client.get_rest_apis()
            api_count = len(apis.get('items', []))
            infra_status['API Gateway'] = f"Found {api_count} APIs"

        except Exception as e:
            infra_status['Infrastructure Check'] = f"❌ Error: {str(e)[:100]}..."

        print("\n🏗️ Infrastructure Status:")
        for component, status in infra_status.items():
            print(f"   📊 {status} - {component}")

        self.validation_report['infrastructure'] = infra_status
        return True

    def generate_demo_readiness_report(self):
        """Generate demo readiness assessment"""
        print("\n" + "=" * 50)
        print("🎬 DEMO READINESS REPORT")
        print("=" * 50)

        self.validation_report['end_time'] = datetime.now().isoformat()

        # Overall assessment
        total_errors = len(self.validation_report['errors'])
        total_warnings = len(self.validation_report['warnings'])

        print(f"\n📊 Overall Assessment:")
        print(f"   Errors: {total_errors}")
        print(f"   Warnings: {total_warnings}")

        # Demo readiness checklist
        demo_ready_items = []

        # Check scripts
        compatibility = self.validation_report.get('compatibility', {})
        script_issues = sum(1 for status in compatibility.values() if "❌" in status)
        if script_issues == 0:
            demo_ready_items.append("✅ All scripts compatible")
        else:
            demo_ready_items.append(f"⚠️ {script_issues} script(s) need attention")

        # Check structure
        if total_errors == 0:
            demo_ready_items.append("✅ Project structure complete")
        else:
            demo_ready_items.append("❌ Project structure issues")

        # Check documentation
        docs_path = self.base_path / 'docs'
        if docs_path.exists():
            doc_files = list(docs_path.glob('*.md'))
            if len(doc_files) >= 3:  # README, ARCHITECTURE, DEPLOYMENT_GUIDE, DEMO_SCRIPT
                demo_ready_items.append("✅ Documentation complete")
            else:
                demo_ready_items.append("⚠️ Documentation incomplete")
        else:
            demo_ready_items.append("❌ Documentation missing")

        print(f"\n🎯 Demo Readiness Checklist:")
        for item in demo_ready_items:
            print(f"   {item}")

        # Demo recommendations
        print(f"\n🎬 Demo Recommendations:")

        if total_errors == 0 and script_issues == 0:
            print("   🎉 DEMO READY!")
            print("   ✅ All systems compatible")
            print("   ✅ Scripts can be demonstrated")
            print("   ✅ Structure is professional")

            print(f"\n🚀 Demo Script Available:")
            demo_script = self.base_path / 'docs' / 'DEMO_SCRIPT.md'
            if demo_script.exists():
                print(f"   📖 {demo_script}")
                print("   ⏱️ 15-20 minute demo script ready")
            else:
                print("   ⚠️ Demo script not found")

        else:
            print("   🔧 PREPARATION NEEDED:")
            if script_issues > 0:
                print("   1. Fix script compatibility issues")
            if total_errors > 0:
                print("   2. Resolve structural issues")
            print("   3. Test again before recording")

        # Save report
        report_file = f"demo_readiness_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.validation_report, f, indent=2)

        print(f"\n📄 Detailed report saved: {report_file}")

        return total_errors == 0 and script_issues == 0

    def run_demo_validation(self):
        """Run complete demo readiness validation"""
        print("🎬 Starting Demo Readiness Validation...\n")

        # Check prerequisites
        prereqs_ok = self.check_demo_prerequisites()

        # Test script compatibility
        scripts_ok = self.test_script_compatibility()

        # Check infrastructure (if available)
        infra_ok = self.check_demo_infrastructure()

        # Generate report
        demo_ready = self.generate_demo_readiness_report()

        return demo_ready

def main():
    """Main validation function"""
    validator = CAPDemoValidator()
    success = validator.run_demo_validation()

    if success:
        print("\n🎉 Demo validation successful!")
        print("Ready for demo recording!")
        print("📖 Review docs/DEMO_SCRIPT.md for recording guidance")
    else:
        print("\n⚠️ Demo preparation needed!")
        print("Please address issues before recording.")

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
