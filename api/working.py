#!/usr/bin/env python3
"""
Simple working Vercel serverless function
"""

import json
from datetime import datetime

def handler(event, context):
    """Simple Vercel serverless handler"""
    
    try:
        # Get the path from the event
        path = event.get('path', '/')
        
        # Set CORS headers
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        
        # Route based on path
        if path == '/' or path == '/api/health':
            response = {
                'status': 'success',
                'message': 'PyTech Arena API is working!',
                'app': 'PyTech Arena Placement System',
                'version': '1.0.0',
                'timestamp': datetime.utcnow().isoformat(),
                'url': 'https://teamx-seven.vercel.app'
            }
            
        elif path == '/api/admin/dashboard':
            response = {
                'status': 'success',
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
            
        elif path == '/api/admin/analytics':
            response = {
                'status': 'success',
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
            
        elif path == '/api/admin/export':
            response = {
                'status': 'success',
                'data': {
                    'csv_content': 'Name,Email,Department,GPA\\nDr. Ramesh Kumar,placement@jntugv.edu.in,Admin,N/A\\nArun Kumar,arun.kumar@jntugv.edu.in,Computer Science,9.0',
                    'filename': f'pytech_arena_{datetime.now().strftime("%Y%m%d")}.csv'
                }
            }
            
        else:
            response = {
                'status': 'error',
                'message': 'Endpoint not found',
                'path': path
            }
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps(response)
            }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }
