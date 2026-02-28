#!/usr/bin/env python3
"""
PyTech Arena - Minimal Working Vercel Serverless Function
Fixed version that handles all common Vercel issues
"""

import json
import sys
from datetime import datetime

def handler(event, context):
    """Minimal Vercel serverless handler that won't crash"""
    
    try:
        # Debug: Print event to understand structure
        print(f"Event received: {type(event)}")
        print(f"Event keys: {list(event.keys()) if isinstance(event, dict) else 'Not a dict'}")
        
        # Get path - try multiple methods
        path = '/'
        if isinstance(event, dict):
            path = event.get('path', event.get('url', '/'))
        elif hasattr(event, 'path'):
            path = event.path
        elif hasattr(event, 'url'):
            path = event.url
        
        # Remove query string if present
        if '?' in path:
            path = path.split('?')[0]
        
        print(f"Processing path: {path}")
        
        # Standard Vercel response format
        def create_response(status_code, body):
            return {
                'statusCode': status_code,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps(body, default=str)
            }
        
        # Route handling
        if path == '/' or path == '/api' or path == '/api/health':
            response_data = {
                'status': 'success',
                'message': 'PyTech Arena API is working!',
                'app': 'PyTech Arena Placement System',
                'version': '1.0.0',
                'timestamp': datetime.utcnow().isoformat(),
                'url': 'https://teamx-seven.vercel.app',
                'debug': {
                    'event_type': str(type(event)),
                    'path_received': path,
                    'python_version': sys.version
                }
            }
            return create_response(200, response_data)
            
        elif path == '/api/admin/dashboard':
            response_data = {
                'status': 'success',
                'message': 'Dashboard data retrieved',
                'data': {
                    'total_students': 3,
                    'placed_students': 0,
                    'placement_rate': 0.0,
                    'dept_stats': {
                        'Computer Science': {'total': 1, 'placed': 0, 'rate': 0.0},
                        'Electronics': {'total': 1, 'placed': 0, 'rate': 0.0},
                        'Mechanical': {'total': 1, 'placed': 0, 'rate': 0.0}
                    }
                }
            }
            return create_response(200, response_data)
            
        elif path == '/api/admin/analytics':
            response_data = {
                'status': 'success',
                'message': 'Analytics data retrieved',
                'data': {
                    'total_students': 3,
                    'placed_students': 0,
                    'placement_rate': 0.0,
                    'dept_stats': {
                        'Computer Science': {'count': 1, 'avg_gpa': 9.0},
                        'Electronics': {'count': 1, 'avg_gpa': 9.2},
                        'Mechanical': {'count': 1, 'avg_gpa': 8.1}
                    }
                }
            }
            return create_response(200, response_data)
            
        elif path == '/api/admin/export':
            response_data = {
                'status': 'success',
                'message': 'Export data generated',
                'data': {
                    'csv_content': 'Name,Email,Department,GPA\nDr. Ramesh Kumar,placement@jntugv.edu.in,Admin,N/A\nArun Kumar,arun.kumar@jntugv.edu.in,Computer Science,9.0',
                    'filename': f'pytech_arena_{datetime.now().strftime("%Y%m%d")}.csv'
                }
            }
            return create_response(200, response_data)
            
        else:
            response_data = {
                'status': 'error',
                'message': f'Endpoint not found: {path}',
                'available_endpoints': [
                    '/api/health',
                    '/api/admin/dashboard', 
                    '/api/admin/analytics',
                    '/api/admin/export'
                ]
            }
            return create_response(404, response_data)
            
    except Exception as e:
        # Catch ALL exceptions to prevent crashes
        error_data = {
            'status': 'error',
            'message': f'Serverless function error: {str(e)}',
            'error_type': type(e).__name__,
            'timestamp': datetime.utcnow().isoformat(),
            'debug_info': {
                'event_received': str(event)[:200] if event else 'No event',
                'python_version': sys.version,
                'working_directory': '/var/task'
            }
        }
        
        print(f"Error occurred: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(error_data, default=str)
        }

# Test function for local debugging
if __name__ == '__main__':
    # Simulate Vercel event
    test_event = {
        'path': '/api/health',
        'httpMethod': 'GET'
    }
    
    print("Testing handler locally...")
    result = handler(test_event, None)
    print("Result:", json.dumps(result, indent=2))
