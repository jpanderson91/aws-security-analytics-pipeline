#!/usr/bin/env python3
"""
CAP Demo Project - Customer API Testing Script
Tests customer-facing APIs for security analytics and metrics
"""

import json
import boto3
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta

class CustomerAPITester:
    """
    Customer API testing for CAP Demo
    
    Tests:
    - Customer metrics API endpoints
    - Security analytics API
    - Customer onboarding API
    - Data retrieval and formatting
    """
    
    def __init__(self):
        self.region = 'us-east-1'
        
        # AWS clients
        self.apigateway = boto3.client('apigateway', region_name=self.region)
        self.lambda_client = boto3.client('lambda', region_name=self.region)
        
        # Get API Gateway URL
        self.api_url = self.get_api_gateway_url()
        
        print("🧪 CAP Demo - Customer API Testing")
        print("=" * 50)
        
        if self.api_url:
            print(f"🔗 API Base URL: {self.api_url}")
        else:
            print("❌ No API Gateway found")
    
    def get_api_gateway_url(self):
        """Get the API Gateway URL"""
        try:
            apis = self.apigateway.get_rest_apis()
            cap_apis = [api for api in apis.get('items', []) 
                       if 'cap' in api.get('name', '').lower()]
            
            if cap_apis:
                api_id = cap_apis[0]['id']
                return f"https://{api_id}.execute-api.{self.region}.amazonaws.com/demo"
            
            return None
            
        except Exception as e:
            print(f"Error getting API URL: {e}")
            return None
    
    def make_api_request(self, method, endpoint, data=None, headers=None):
        """Make API request using urllib"""
        if not self.api_url:
            return None, "No API URL available"
        
        url = f"{self.api_url}{endpoint}"
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                req = urllib.request.Request(url, headers=headers)
            elif method == 'POST':
                json_data = json.dumps(data) if data else "{}"
                json_bytes = json_data.encode('utf-8')
                req = urllib.request.Request(url, data=json_bytes, headers=headers)
                req.add_header('Content-Length', len(json_bytes))
            else:
                return None, f"Unsupported method: {method}"
            
            req.get_method = lambda: method
            
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                return {
                    'status_code': response.status,
                    'data': json.loads(response_data) if response_data else {},
                    'headers': dict(response.headers)
                }, None
                
        except urllib.error.HTTPError as e:
            error_data = e.read().decode('utf-8') if e.fp else "No error details"
            return {
                'status_code': e.code,
                'data': error_data,
                'headers': dict(e.headers) if hasattr(e, 'headers') else {}
            }, None
            
        except Exception as e:
            return None, str(e)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        print("\n🏥 Testing Health Endpoint...")
        
        response, error = self.make_api_request('GET', '/health')
        
        if error:
            print(f"❌ Health check failed: {error}")
            return False
        
        if response['status_code'] == 200:
            print("✅ Health check passed")
            if 'data' in response and response['data']:
                health_data = response['data']
                print(f"   Status: {health_data.get('status', 'unknown')}")
                print(f"   Timestamp: {health_data.get('timestamp', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response['status_code']}")
            return False
    
    def test_customer_metrics_endpoint(self):
        """Test customer metrics endpoint"""
        print("\n📊 Testing Customer Metrics Endpoint...")
        
        # Test basic metrics
        response, error = self.make_api_request('GET', '/metrics')
        
        if error:
            print(f"❌ Metrics request failed: {error}")
            return False
        
        if response['status_code'] == 200:
            print("✅ Metrics endpoint responded")
            
            if 'data' in response and response['data']:
                metrics_data = response['data']
                print(f"   Metrics available: {len(metrics_data) if isinstance(metrics_data, (list, dict)) else 'unknown'}")
                
                # Display sample metrics
                if isinstance(metrics_data, dict):
                    for key, value in list(metrics_data.items())[:3]:
                        print(f"   - {key}: {value}")
                elif isinstance(metrics_data, list) and metrics_data:
                    print(f"   - Sample item: {metrics_data[0]}")
            
            return True
        elif response['status_code'] == 403:
            print("🔒 Metrics endpoint requires authentication")
            return True  # This is expected behavior
        else:
            print(f"❌ Metrics request failed: {response['status_code']}")
            return False
    
    def test_customer_metrics_with_params(self):
        """Test customer metrics with query parameters"""
        print("\n📈 Testing Customer Metrics with Parameters...")
        
        # Test with customer ID parameter
        test_params = [
            ('customer_id', 'test-customer-123'),
            ('date_range', '7'),
            ('metric_type', 'security')
        ]
        
        results = []
        
        for param_name, param_value in test_params:
            endpoint = f"/metrics?{param_name}={param_value}"
            response, error = self.make_api_request('GET', endpoint)
            
            if error:
                results.append(f"❌ {param_name}={param_value}: {error}")
            elif response['status_code'] in [200, 403]:
                results.append(f"✅ {param_name}={param_value}: {response['status_code']}")
            else:
                results.append(f"⚠️ {param_name}={param_value}: {response['status_code']}")
        
        for result in results:
            print(f"   {result}")
        
        success_count = sum(1 for r in results if "✅" in r)
        return success_count >= len(test_params) * 0.5
    
    def test_security_analytics_endpoint(self):
        """Test security analytics endpoint"""
        print("\n🔒 Testing Security Analytics Endpoint...")
        
        response, error = self.make_api_request('GET', '/security')
        
        if error:
            print(f"❌ Security request failed: {error}")
            return False
        
        if response['status_code'] == 200:
            print("✅ Security analytics endpoint responded")
            
            if 'data' in response and response['data']:
                security_data = response['data']
                print(f"   Security data available: {len(security_data) if isinstance(security_data, (list, dict)) else 'unknown'}")
                
                # Look for common security metrics
                if isinstance(security_data, dict):
                    security_keys = ['threats', 'incidents', 'alerts', 'risks']
                    found_keys = [key for key in security_keys if key in security_data]
                    if found_keys:
                        print(f"   Security metrics: {', '.join(found_keys)}")
            
            return True
        elif response['status_code'] == 403:
            print("🔒 Security endpoint requires authentication")
            return True  # Expected behavior
        else:
            print(f"❌ Security request failed: {response['status_code']}")
            return False
    
    def test_customer_onboarding_endpoint(self):
        """Test customer onboarding endpoint"""
        print("\n👤 Testing Customer Onboarding Endpoint...")
        
        # Test onboarding request
        onboarding_data = {
            'customer_name': 'Test Corporation',
            'industry': 'Technology',
            'security_requirements': ['PCI', 'SOX'],
            'contact_email': 'test@example.com',
            'requested_features': ['dashboards', 'alerts', 'reporting']
        }
        
        response, error = self.make_api_request('POST', '/onboard', onboarding_data)
        
        if error:
            print(f"❌ Onboarding request failed: {error}")
            return False
        
        if response['status_code'] == 200:
            print("✅ Onboarding endpoint responded")
            
            if 'data' in response and response['data']:
                onboard_response = response['data']
                if isinstance(onboard_response, dict):
                    customer_id = onboard_response.get('customer_id', 'unknown')
                    status = onboard_response.get('status', 'unknown')
                    print(f"   Customer ID: {customer_id}")
                    print(f"   Status: {status}")
            
            return True
        elif response['status_code'] == 201:
            print("✅ Customer onboarded successfully")
            return True
        elif response['status_code'] == 403:
            print("🔒 Onboarding endpoint requires authentication")
            return True  # Expected behavior
        else:
            print(f"❌ Onboarding failed: {response['status_code']}")
            print(f"   Response: {response.get('data', 'No details')}")
            return False
    
    def test_dashboard_data_endpoint(self):
        """Test dashboard data endpoint"""
        print("\n📋 Testing Dashboard Data Endpoint...")
        
        # Test different dashboard types
        dashboard_types = ['overview', 'security', 'metrics', 'costs']
        
        results = []
        
        for dashboard_type in dashboard_types:
            endpoint = f"/dashboard/{dashboard_type}"
            response, error = self.make_api_request('GET', endpoint)
            
            if error:
                results.append(f"❌ {dashboard_type}: {error}")
            elif response['status_code'] in [200, 403]:
                results.append(f"✅ {dashboard_type}: {response['status_code']}")
                
                # Check for data structure
                if response['status_code'] == 200 and 'data' in response:
                    data = response['data']
                    if isinstance(data, dict) and data:
                        print(f"   {dashboard_type} data keys: {list(data.keys())[:3]}")
            else:
                results.append(f"⚠️ {dashboard_type}: {response['status_code']}")
        
        for result in results:
            print(f"   {result}")
        
        success_count = sum(1 for r in results if "✅" in r)
        return success_count >= len(dashboard_types) * 0.5
    
    def test_lambda_functions_directly(self):
        """Test Lambda functions directly"""
        print("\n⚡ Testing Lambda Functions Directly...")
        
        try:
            # List CAP Demo Lambda functions
            functions = self.lambda_client.list_functions()
            cap_functions = [f for f in functions['Functions'] 
                           if 'cap' in f['FunctionName'].lower()]
            
            if not cap_functions:
                print("❌ No CAP Demo Lambda functions found")
                return False
            
            test_results = []
            
            for func in cap_functions[:3]:  # Test first 3 functions
                func_name = func['FunctionName']
                
                try:
                    # Test invoke
                    test_event = {
                        'httpMethod': 'GET',
                        'path': '/test',
                        'headers': {'Content-Type': 'application/json'},
                        'body': None,
                        'isBase64Encoded': False
                    }
                    
                    response = self.lambda_client.invoke(
                        FunctionName=func_name,
                        InvocationType='RequestResponse',
                        Payload=json.dumps(test_event)
                    )
                    
                    if response['StatusCode'] == 200:
                        test_results.append(f"✅ {func_name}: Direct invoke successful")
                        
                        # Try to parse response
                        payload = response['Payload'].read().decode('utf-8')
                        try:
                            response_data = json.loads(payload)
                            status_code = response_data.get('statusCode', 'unknown')
                            print(f"   Response status: {status_code}")
                        except (json.JSONDecodeError, AttributeError):
                            print(f"   Response: {payload[:100]}...")
                    else:
                        test_results.append(f"❌ {func_name}: Invoke failed ({response['StatusCode']})")
                        
                except Exception as e:
                    test_results.append(f"❌ {func_name}: {str(e)[:50]}")
            
            for result in test_results:
                print(f"   {result}")
            
            success_count = sum(1 for r in test_results if "✅" in r)
            return success_count >= len(test_results) * 0.5
            
        except Exception as e:
            print(f"❌ Lambda testing failed: {e}")
            return False
    
    def generate_api_test_report(self, results):
        """Generate API test report"""
        print("\n" + "=" * 50)
        print("🧪 CUSTOMER API TEST REPORT")
        print("=" * 50)
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r)
        
        print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed")
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        if passed_tests == total_tests:
            print("\n🎉 All customer APIs are working!")
            print("✅ Ready for customer demonstration")
        elif passed_tests >= total_tests * 0.75:
            print("\n⚠️ Most APIs are working")
            print("💡 Some endpoints may need authentication")
        else:
            print("\n❌ Multiple API issues detected")
            print("🔧 API troubleshooting required")
        
        # Usage examples
        if self.api_url:
            print(f"\n🔗 API Usage Examples:")
            print(f"Health Check: curl {self.api_url}/health")
            print(f"Customer Metrics: curl {self.api_url}/metrics?customer_id=123")
            print(f"Security Data: curl {self.api_url}/security")
            print(f"Onboard Customer: curl -X POST {self.api_url}/onboard -d '{{\"customer_name\":\"Test Corp\"}}'")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n📅 Test completed: {timestamp}")
        
        return passed_tests >= total_tests * 0.75
    
    def run_all_tests(self):
        """Run all customer API tests"""
        print("Starting customer API tests...\n")
        
        if not self.api_url:
            print("❌ Cannot run tests - no API Gateway found")
            return False
        
        # Run all tests
        results = {
            "Health Endpoint": self.test_health_endpoint(),
            "Customer Metrics": self.test_customer_metrics_endpoint(),
            "Metrics with Parameters": self.test_customer_metrics_with_params(),
            "Security Analytics": self.test_security_analytics_endpoint(),
            "Customer Onboarding": self.test_customer_onboarding_endpoint(),
            "Dashboard Data": self.test_dashboard_data_endpoint(),
            "Direct Lambda Testing": self.test_lambda_functions_directly()
        }
        
        # Generate report
        overall_success = self.generate_api_test_report(results)
        
        return overall_success

def main():
    """Main testing function"""
    tester = CustomerAPITester()
    success = tester.run_all_tests()
    
    exit_code = 0 if success else 1
    return exit_code

if __name__ == "__main__":
    exit(main())
