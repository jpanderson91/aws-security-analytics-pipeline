"""
CAP Demo - Customer Metrics API Lambda Function
Provides customer-facing API for accessing performance metrics and analytics
"""

import json
import boto3
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
athena_client = boto3.client('athena')
s3_client = boto3.client('s3')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle API Gateway requests for customer metrics data
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    
    try:
        logger.info(f"Processing metrics API request: {json.dumps(event)}")
        
        # Extract customer ID from path parameters
        customer_id = event.get('pathParameters', {}).get('customer_id')
        if not customer_id:
            return create_error_response(400, "Missing customer_id parameter")
        
        # Extract query parameters
        query_params = event.get('queryStringParameters') or {}
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        metric_type = query_params.get('metric_type')
        
        # Set default date range (last 7 days)
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Get HTTP method
        http_method = event.get('httpMethod', 'GET')
        
        if http_method == 'GET':
            return handle_get_metrics(customer_id, start_date, end_date, metric_type)
        else:
            return create_error_response(405, f"Method {http_method} not allowed")
            
    except Exception as e:
        logger.error(f"Error processing metrics API request: {str(e)}")
        return create_error_response(500, "Internal server error")

def handle_get_metrics(customer_id: str, start_date: str, end_date: str, metric_type: Optional[str]) -> Dict[str, Any]:
    """
    Handle GET request for customer metrics
    
    Args:
        customer_id: Customer identifier
        start_date: Start date for metrics (YYYY-MM-DD)
        end_date: End date for metrics (YYYY-MM-DD)
        metric_type: Optional filter for specific metric type
        
    Returns:
        API response with metrics data
    """
    
    try:
        # Build Athena query
        query = build_metrics_query(customer_id, start_date, end_date, metric_type)
        
        # Execute Athena query
        query_result = execute_athena_query(query)
        
        # Process and format results
        metrics_data = process_metrics_results(query_result)
        
        # Calculate summary statistics
        summary = calculate_metrics_summary(metrics_data)
        
        response_data = {
            'customer_id': customer_id,
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'filters': {
                'metric_type': metric_type
            },
            'summary': summary,
            'metrics': metrics_data,
            'metadata': {
                'total_records': len(metrics_data),
                'query_timestamp': datetime.now().isoformat(),
                'data_source': 'silver_layer'
            }
        }
        
        return create_success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error handling GET metrics: {str(e)}")
        return create_error_response(500, f"Error retrieving metrics: {str(e)}")

def build_metrics_query(customer_id: str, start_date: str, end_date: str, metric_type: Optional[str]) -> str:
    """
    Build Athena SQL query for metrics data
    
    Args:
        customer_id: Customer identifier
        start_date: Start date for metrics
        end_date: End date for metrics
        metric_type: Optional metric type filter
        
    Returns:
        SQL query string
    """
    
    database_name = os.getenv('ATHENA_DATABASE', 'cap_demo_data_lake')
    
    base_query = f"""
    SELECT 
        customer_id,
        metric_type,
        window,
        metric_date,
        metric_hour,
        overall_avg,
        overall_min,
        overall_max,
        avg_p95,
        avg_p99,
        measurement_count
    FROM "{database_name}"."application_metrics_silver"
    WHERE customer_id = '{customer_id}'
      AND date >= '{start_date.replace('-', '/')}'
      AND date <= '{end_date.replace('-', '/')}'
    """
    
    if metric_type:
        base_query += f" AND metric_type = '{metric_type}'"
    
    base_query += " ORDER BY metric_date DESC, metric_hour DESC, metric_type"
    
    return base_query

def execute_athena_query(query: str) -> Dict[str, Any]:
    """
    Execute Athena query and return results
    
    Args:
        query: SQL query to execute
        
    Returns:
        Query results
    """
    
    try:
        workgroup = os.getenv('ATHENA_WORKGROUP', 'cap-demo-analytics')
        
        # Start query execution
        response = athena_client.start_query_execution(
            QueryString=query,
            WorkGroup=workgroup
        )
        
        query_execution_id = response['QueryExecutionId']
        
        # Wait for query to complete
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            query_status = athena_client.get_query_execution(
                QueryExecutionId=query_execution_id
            )
            
            status = query_status['QueryExecution']['Status']['State']
            
            if status == 'SUCCEEDED':
                break
            elif status in ['FAILED', 'CANCELLED']:
                raise Exception(f"Query failed with status: {status}")
            
            attempt += 1
            if attempt >= max_attempts:
                raise Exception("Query timeout")
        
        # Get query results
        results = athena_client.get_query_results(
            QueryExecutionId=query_execution_id
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error executing Athena query: {str(e)}")
        raise

def process_metrics_results(query_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process Athena query results into structured metrics data
    
    Args:
        query_result: Raw Athena query results
        
    Returns:
        Processed metrics data
    """
    
    try:
        rows = query_result.get('ResultSet', {}).get('Rows', [])
        
        if not rows:
            return []
        
        # Extract column names from first row
        columns = [col.get('VarCharValue', '') for col in rows[0].get('Data', [])]
        
        # Process data rows
        metrics_data = []
        for row in rows[1:]:  # Skip header row
            row_data = {}
            for i, col in enumerate(row.get('Data', [])):
                column_name = columns[i] if i < len(columns) else f'col_{i}'
                value = col.get('VarCharValue', '')
                
                # Convert numeric values
                if column_name in ['overall_avg', 'overall_min', 'overall_max', 'avg_p95', 'avg_p99']:
                    try:
                        row_data[column_name] = float(value) if value else 0.0
                    except ValueError:
                        row_data[column_name] = 0.0
                elif column_name in ['measurement_count', 'metric_hour']:
                    try:
                        row_data[column_name] = int(value) if value else 0
                    except ValueError:
                        row_data[column_name] = 0
                else:
                    row_data[column_name] = value
            
            metrics_data.append(row_data)
        
        return metrics_data
        
    except Exception as e:
        logger.error(f"Error processing metrics results: {str(e)}")
        return []

def calculate_metrics_summary(metrics_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate summary statistics for metrics data
    
    Args:
        metrics_data: Processed metrics data
        
    Returns:
        Summary statistics
    """
    
    try:
        if not metrics_data:
            return {}
        
        # Group by metric type
        metric_types = {}
        for record in metrics_data:
            metric_type = record.get('metric_type', 'unknown')
            if metric_type not in metric_types:
                metric_types[metric_type] = []
            metric_types[metric_type].append(record)
        
        # Calculate summaries for each metric type
        summary = {}
        for metric_type, records in metric_types.items():
            avg_values = [r.get('overall_avg', 0) for r in records if r.get('overall_avg') is not None]
            p95_values = [r.get('avg_p95', 0) for r in records if r.get('avg_p95') is not None]
            
            if avg_values:
                summary[metric_type] = {
                    'record_count': len(records),
                    'avg_value': sum(avg_values) / len(avg_values),
                    'min_value': min(avg_values),
                    'max_value': max(avg_values),
                    'avg_p95': sum(p95_values) / len(p95_values) if p95_values else 0,
                    'latest_timestamp': max([r.get('metric_date', '') for r in records])
                }
        
        # Overall summary
        overall_summary = {
            'total_metric_types': len(metric_types),
            'total_records': len(metrics_data),
            'metric_types': list(metric_types.keys()),
            'by_type': summary
        }
        
        return overall_summary
        
    except Exception as e:
        logger.error(f"Error calculating metrics summary: {str(e)}")
        return {}

def create_success_response(data: Any) -> Dict[str, Any]:
    """Create successful API response"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        },
        'body': json.dumps(data, default=str)
    }

def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Create error API response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'error': message,
            'timestamp': datetime.now().isoformat()
        })
    }
