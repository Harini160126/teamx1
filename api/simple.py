#!/usr/bin/env python3
"""
Simple Vercel handler without Flask dependencies
"""

import json
from datetime import datetime

def handler(request):
    """Simple Vercel serverless handler"""
    try:
        # Parse request
        method = request.method
        path = request.path
        
        # Simple responses
        if path == '/' or path == '/api/health':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'status': 'success',
                    'message': 'PyTech Arena API is running',
                    'timestamp': datetime.utcnow().isoformat(),
                    'version': '1.0.0'
                })
            }
        
        elif path == '/api/admin/dashboard':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'status': 'success',
                    'data': {
                        'total_students': 3,
                        'placed_students': 0,
                        'placement_rate': 0.0,
                        'dept_stats': {
                            'Computer Science': {'total': 1, 'placed': 0, 'placement_rate': 0.0},
                            'Electronics': {'total': 1, 'placed': 0, 'placement_rate': 0.0},
                            'Mechanical': {'total': 1, 'placed': 0, 'placement_rate': 0.0}
                        }
                    }
                })
            }
        
        elif path == '/api/admin/analytics':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'status': 'success',
                    'data': {
                        'total_students': 3,
                        'placed_students': 0,
                        'not_placed_students': 3,
                        'placement_rate': 0.0,
                        'dept_stats': {
                            'Computer Science': {'count': 1, 'avg_gpa': 9.0},
                            'Electronics': {'count': 1, 'avg_gpa': 9.2},
                            'Mechanical': {'count': 1, 'avg_gpa': 8.1}
                        }
                    }
                })
            }
        
        elif path == '/api/admin/export':
            csv_content = """PyTech Arena Student Report
Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """

Name,Email,Department,GPA,Placement Status
Dr. Ramesh Kumar,placement@jntugv.edu.in,Admin,N/A,Placed
Arun Kumar,arun.kumar@jntugv.edu.in,Computer Science,9.0,Not Placed
Priya Sharma,priya.sharma@jntugv.edu.in,Electronics,9.2,Not Placed
Rahul Verma,rahul.verma@jntugv.edu.in,Mechanical,8.1,Not Placed"""
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'status': 'success',
                    'data': {
                        'csv_content': csv_content,
                        'filename': f'pytech_arena_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                    }
                })
            }
        
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'status': 'error',
                    'message': 'Endpoint not found'
                })
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
                'message': f'Serverless function error: {str(e)}'
            })
        }
