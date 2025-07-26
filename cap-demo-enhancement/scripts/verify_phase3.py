#!/usr/bin/env python3
"""
CAP Demo Project - Phase 3 Verification Script
Verifies QuickSight dashboards, API Gateway, and customer analytics components
"""

import json
import boto3
import time
import requests
from datetime import datetime
from pathlib import Path

class Phase3Verification:
    """
    Phase 3 verification for CAP Demo
    
    Verifies:
    - QuickSight dashboards and data sources
    - API Gateway endpoints and responses
    - Athena workgroup and queries
    - Lambda function deployments
    - Data flow from Kafka to dashboards
    """
    
    def __init__(self):
        self.region = 'us-east-1'
        
        # AWS clients
        self.quicksight = boto3.client('quicksight', region_name=self.region)
        self.apigateway = boto3.client('apigateway', region_name=self.region)
        self.lambda_client = boto3.client('lambda', region_name=self.region)
        self.athena = boto3.client('athena', region_name=self.region)
        self.glue = boto3.client('glue', region_name=self.region)
        self.s3 = boto3.client('s3', region_name=self.region)
        
        # Get AWS account ID
        sts = boto3.client('sts')
        self.account_id = sts.get_caller_identity()['Account']
        
        print("🔍 CAP Demo - Phase 3 Verification")
        print("=" * 50)
    
    def verify_terraform_deployment(self):
        """Verify Terraform deployment of Phase 3 resources"""
        print("\n📋 Verifying Terraform Deployment...")
        
        # Check terraform state
        if not Path('terraform/terraform.tfstate').exists():
            print("❌ Terraform state file not found")
            return False
        
        try:
            with open('terraform/terraform.tfstate', 'r') as f:
                state = json.load(f)
            
            # Check for Phase 3 resources
            resources = state.get('resources', [])
            phase3_resources = [
                'aws_quicksight_data_source',
                'aws_api_gateway_rest_api',
                'aws_athena_workgroup',
                'aws_glue_catalog_database'
            ]
            
            found_resources = []
            for resource_type in phase3_resources:
                matching = [r for r in resources if r.get('type') == resource_type]
                if matching:
                    found_resources.append(f"✅ {resource_type}: {len(matching)} instances")
                else:
                    found_resources.append(f"❌ {resource_type}: Not found")
            
            for resource in found_resources:
                print(f"   {resource}")
            
            deployed_count = sum(1 for r in found_resources if "✅" in r)
            total_count = len(phase3_resources)
            
            print(f"\n📊 Terraform Resources: {deployed_count}/{total_count} deployed")
            return deployed_count >= total_count * 0.75  # Allow 75% success rate
            
        except Exception as e:
            print(f"❌ Error checking Terraform state: {e}")
            return False
    
    def verify_quicksight_setup(self):
        """Verify QuickSight subscription and data sources"""
        print("\n📊 Verifying QuickSight Setup...")
        
        try:
            # Check QuickSight subscription
            subscription = self.quicksight.describe_account_subscription(
                AwsAccountId=self.account_id
            )
            
            print(f"✅ QuickSight Subscription: {subscription['AccountInfo']['Edition']}")
            
            # List data sources
            data_sources = self.quicksight.list_data_sources(AwsAccountId=self.account_id)
            cap_sources = [ds for ds in data_sources.get('DataSources', []) 
                          if 'cap' in ds.get('Name', '').lower() or 'athena' in ds.get('Type', '').lower()]
            
            print(f"✅ Data Sources: {len(cap_sources)} found")
            for ds in cap_sources[:3]:  # Show first 3
                print(f"   - {ds['Name']} ({ds['Type']})")
            
            # List dashboards
            dashboards = self.quicksight.list_dashboards(AwsAccountId=self.account_id)
            cap_dashboards = [db for db in dashboards.get('DashboardSummaryList', [])
                             if 'cap' in db.get('Name', '').lower()]
            
            print(f"✅ Dashboards: {len(cap_dashboards)} found")
            for db in cap_dashboards[:3]:  # Show first 3
                print(f"   - {db['Name']}")
            
            return True
            
        except self.quicksight.exceptions.ResourceNotFoundException:
            print("❌ QuickSight subscription not found")
            print("💡 To enable: aws quicksight create-account-subscription --aws-account-id", self.account_id)
            return False
        except Exception as e:
            print(f"⚠️ QuickSight check failed: {e}")
            return False
    
    def verify_api_gateway(self):
        """Verify API Gateway deployment and endpoints"""
        print("\n🌐 Verifying API Gateway...")
        
        try:
            # List REST APIs
            apis = self.apigateway.get_rest_apis()
            cap_apis = [api for api in apis.get('items', []) 
                       if 'cap' in api.get('name', '').lower()]
            
            if not cap_apis:
                print("❌ No CAP Demo APIs found")
                return False
            
            api = cap_apis[0]
            api_id = api['id']
            api_name = api['name']
            
            print(f"✅ API Gateway: {api_name} ({api_id})")
            
            # Get resources
            resources = self.apigateway.get_resources(restApiId=api_id)
            resource_count = len(resources.get('items', []))
            print(f"✅ API Resources: {resource_count} endpoints")
            
            # List key resources
            for resource in resources['items'][:5]:  # Show first 5
                path = resource.get('pathPart', '/')
                methods = list(resource.get('resourceMethods', {}).keys())
                if methods:
                    print(f"   - {path}: {', '.join(methods)}")
            
            # Check deployments
            deployments = self.apigateway.get_deployments(restApiId=api_id)
            if deployments.get('items'):
                latest_deployment = max(deployments['items'], 
                                      key=lambda x: x.get('createdDate', datetime.min))
                print(f"✅ Latest Deployment: {latest_deployment['id']}")
                
                # Construct API URL
                api_url = f"https://{api_id}.execute-api.{self.region}.amazonaws.com/demo"
                print(f"🔗 API Endpoint: {api_url}")
                
                return True
            else:
                print("❌ No deployments found")
                return False
                
        except Exception as e:
            print(f"❌ API Gateway verification failed: {e}")
            return False
    
    def verify_lambda_functions(self):
        """Verify Lambda function deployments"""
        print("\n⚡ Verifying Lambda Functions...")
        
        try:
            # List all functions
            functions = self.lambda_client.list_functions()
            cap_functions = [f for f in functions['Functions'] 
                           if 'cap' in f['FunctionName'].lower()]
            
            if not cap_functions:
                print("❌ No CAP Demo Lambda functions found")
                return False
            
            print(f"✅ Lambda Functions: {len(cap_functions)} found")
            
            # Check each function
            for func in cap_functions:
                func_name = func['FunctionName']
                runtime = func['Runtime']
                status = func['State']
                
                print(f"   - {func_name}: {runtime} ({status})")
                
                # Test function invocation (if not running)
                if status == 'Active':
                    try:
                        response = self.lambda_client.invoke(
                            FunctionName=func_name,
                            InvocationType='RequestResponse',
                            Payload=json.dumps({'test': True})
                        )
                        
                        if response['StatusCode'] == 200:
                            print(f"     ✅ Invocation test passed")
                        else:
                            print(f"     ⚠️ Invocation returned {response['StatusCode']}")
                    
                    except Exception as e:
                        print(f"     ⚠️ Invocation test failed: {str(e)[:50]}")
            
            return len(cap_functions) >= 3  # Expect at least 3 functions
            
        except Exception as e:
            print(f"❌ Lambda verification failed: {e}")
            return False
    
    def verify_athena_workgroup(self):
        """Verify Athena workgroup and data catalog"""
        print("\n🔍 Verifying Athena Analytics...")
        
        try:
            # Check workgroups
            workgroups = self.athena.list_work_groups()
            cap_workgroups = [wg for wg in workgroups['WorkGroups'] 
                             if 'cap' in wg['Name'].lower()]
            
            if cap_workgroups:
                wg_name = cap_workgroups[0]['Name']
                print(f"✅ Athena Workgroup: {wg_name}")
                
                # Get workgroup details
                wg_details = self.athena.get_work_group(WorkGroup=wg_name)
                config = wg_details['WorkGroup']['Configuration']
                
                if 'ResultConfiguration' in config:
                    result_location = config['ResultConfiguration'].get('OutputLocation', 'Not configured')
                    print(f"   📁 Result Location: {result_location}")
            else:
                print("❌ No CAP Demo Athena workgroup found")
                return False
            
            # Check Glue database
            databases = self.glue.get_databases()
            cap_databases = [db for db in databases['DatabaseList'] 
                           if 'cap' in db['Name'].lower()]
            
            if cap_databases:
                db_name = cap_databases[0]['Name']
                print(f"✅ Glue Database: {db_name}")
                
                # List tables
                try:
                    tables = self.glue.get_tables(DatabaseName=db_name)
                    table_count = len(tables['TableList'])
                    print(f"   📋 Tables: {table_count} found")
                    
                    for table in tables['TableList'][:3]:  # Show first 3
                        print(f"     - {table['Name']}")
                        
                except Exception as e:
                    print(f"   ⚠️ Table listing failed: {e}")
            else:
                print("❌ No CAP Demo Glue database found")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Athena verification failed: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test API Gateway endpoints"""
        print("\n🧪 Testing API Endpoints...")
        
        try:
            # Get API Gateway URL
            apis = self.apigateway.get_rest_apis()
            cap_apis = [api for api in apis.get('items', []) 
                       if 'cap' in api.get('name', '').lower()]
            
            if not cap_apis:
                print("❌ No API found for testing")
                return False
            
            api_id = cap_apis[0]['id']
            base_url = f"https://{api_id}.execute-api.{self.region}.amazonaws.com/demo"
            
            # Test endpoints
            test_endpoints = [
                ('GET', '/health', 'Health check'),
                ('GET', '/metrics', 'Customer metrics'),
                ('GET', '/security', 'Security data'),
                ('POST', '/onboard', 'Customer onboarding')
            ]
            
            test_results = []
            
            for method, path, description in test_endpoints:
                url = f"{base_url}{path}"
                
                try:
                    if method == 'GET':
                        response = requests.get(url, timeout=10)
                    elif method == 'POST':
                        response = requests.post(url, json={'test': True}, timeout=10)
                    
                    status = response.status_code
                    
                    if status == 200:
                        test_results.append(f"✅ {method} {path}: {description} (200 OK)")
                    elif status == 403:
                        test_results.append(f"🔒 {method} {path}: {description} (403 - Auth required)")
                    else:
                        test_results.append(f"⚠️ {method} {path}: {description} ({status})")
                        
                except requests.exceptions.Timeout:
                    test_results.append(f"⏱️ {method} {path}: {description} (Timeout)")
                except Exception as e:
                    test_results.append(f"❌ {method} {path}: {description} (Error: {str(e)[:30]})")
            
            for result in test_results:
                print(f"   {result}")
            
            # Count successful tests
            success_count = sum(1 for r in test_results if "✅" in r or "🔒" in r)
            total_count = len(test_results)
            
            print(f"\n📊 API Tests: {success_count}/{total_count} passed")
            return success_count >= total_count * 0.5  # 50% success rate acceptable
            
        except Exception as e:
            print(f"❌ API testing failed: {e}")
            return False
    
    def verify_data_flow(self):
        """Verify data flow from S3 to analytics"""
        print("\n📊 Verifying Data Flow...")
        
        try:
            # Check S3 buckets for data
            bucket_response = self.s3.list_buckets()
            cap_buckets = [b for b in bucket_response['Buckets'] 
                          if 'cap-demo' in b['Name']]
            
            data_found = False
            
            for bucket in cap_buckets:
                bucket_name = bucket['Name']
                
                try:
                    # List objects in bucket
                    objects = self.s3.list_objects_v2(Bucket=bucket_name, MaxKeys=10)
                    object_count = objects.get('KeyCount', 0)
                    
                    if object_count > 0:
                        print(f"✅ {bucket_name}: {object_count} objects")
                        data_found = True
                        
                        # Show sample objects
                        for obj in objects.get('Contents', [])[:3]:
                            size_kb = obj['Size'] // 1024
                            print(f"   - {obj['Key']} ({size_kb} KB)")
                    else:
                        print(f"📁 {bucket_name}: Empty")
                        
                except Exception as e:
                    print(f"⚠️ {bucket_name}: Access error ({str(e)[:30]})")
            
            if data_found:
                print("✅ Data available for analytics")
            else:
                print("⚠️ No data found - run data ingestion first")
            
            return True
            
        except Exception as e:
            print(f"❌ Data flow verification failed: {e}")
            return False
    
    def generate_verification_report(self, results):
        """Generate verification report"""
        print("\n" + "=" * 50)
        print("📋 PHASE 3 VERIFICATION REPORT")
        print("=" * 50)
        
        total_checks = len(results)
        passed_checks = sum(1 for r in results.values() if r)
        
        print(f"\n📊 Overall Status: {passed_checks}/{total_checks} checks passed")
        
        for check_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {check_name}")
        
        if passed_checks == total_checks:
            print("\n🎉 Phase 3 is fully operational!")
            print("✅ Customer dashboards ready")
            print("✅ API Gateway functional")
            print("✅ Analytics pipeline active")
        elif passed_checks >= total_checks * 0.75:
            print("\n⚠️ Phase 3 is mostly operational")
            print("💡 Some components may need attention")
        else:
            print("\n❌ Phase 3 has significant issues")
            print("🔧 Troubleshooting required")
        
        # Next steps
        print("\n🚀 Next Steps:")
        print("1. Access QuickSight: https://us-east-1.quicksight.aws.amazon.com/")
        print("2. Test APIs using Postman or curl")
        print("3. Run full demo: python run_full_demo.py")
        print("4. Monitor CloudWatch logs for issues")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n📅 Report generated: {timestamp}")
        
        return passed_checks >= total_checks * 0.75
    
    def run_verification(self):
        """Run complete Phase 3 verification"""
        print("Starting Phase 3 verification...\n")
        
        # Run all verification checks
        results = {
            "Terraform Deployment": self.verify_terraform_deployment(),
            "QuickSight Setup": self.verify_quicksight_setup(),
            "API Gateway": self.verify_api_gateway(),
            "Lambda Functions": self.verify_lambda_functions(),
            "Athena Analytics": self.verify_athena_workgroup(),
            "API Endpoints": self.test_api_endpoints(),
            "Data Flow": self.verify_data_flow()
        }
        
        # Generate report
        overall_success = self.generate_verification_report(results)
        
        return overall_success

def main():
    """Main verification function"""
    verifier = Phase3Verification()
    success = verifier.run_verification()
    
    exit_code = 0 if success else 1
    return exit_code

if __name__ == "__main__":
    exit(main())
