#!/usr/bin/env python3
"""
PyTech Arena - Fixed Vercel Serverless Function
Optimized for teamx-seven.vercel.app
"""

import json
from datetime import datetime

def handler(request):
    """Fixed Vercel serverless function handler"""
    
    # Set CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    try:
        # Handle OPTIONS request for CORS
        if request.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Get the path
        path = getattr(request, 'path', '/') or '/'
        
        # Route the request
        if path == '/' or path == '/api' or path == '/api/health':
            response_data = {
                'status': 'success',
                'message': 'PyTech Arena API is running',
                'app': 'PyTech Arena Placement Management System',
                'version': '1.0.0',
                'timestamp': datetime.utcnow().isoformat(),
                'url': 'https://teamx-seven.vercel.app',
                'endpoints': [
                    '/api/health',
                    '/api/admin/dashboard',
                    '/api/admin/analytics',
                    '/api/admin/export'
                ]
            }
            
        elif path == '/api/admin/dashboard':
            response_data = {
                'status': 'success',
                'message': 'Dashboard data retrieved successfully',
                'data': {
                    'total_students': 3,
                    'placed_students': 0,
                    'not_placed_students': 3,
                    'placement_rate': 0.0,
                    'total_recruiters': 3,
                    'active_recruiters': 3,
                    'recruiter_success_rate': 100.0,
                    'dept_stats': {
                        'Computer Science': {
                            'total': 1,
                            'placed': 0,
                            'placement_rate': 0.0,
                            'avg_gpa': 9.0
                        },
                        'Electronics and Communication Engineering': {
                            'total': 1,
                            'placed': 0,
                            'placement_rate': 0.0,
                            'avg_gpa': 9.2
                        },
                        'Mechanical Engineering': {
                            'total': 1,
                            'placed': 0,
                            'placement_rate': 0.0,
                            'avg_gpa': 8.1
                        }
                    },
                    'recent_applications': 0
                }
            }
            
        elif path == '/api/admin/analytics':
            response_data = {
                'status': 'success',
                'message': 'Analytics data retrieved successfully',
                'data': {
                    'total_students': 3,
                    'placed_students': 0,
                    'not_placed_students': 3,
                    'placement_rate': 0.0,
                    'dept_stats': {
                        'Computer Science': {
                            'count': 1,
                            'avg_gpa': 9.0
                        },
                        'Electronics and Communication Engineering': {
                            'count': 1,
                            'avg_gpa': 9.2
                        },
                        'Mechanical Engineering': {
                            'count': 1,
                            'avg_gpa': 8.1
                        }
                    },
                    'total_recruiters': 3,
                    'active_recruiters': 3,
                    'recruiter_success_rate': 100.0,
                    'recent_students': 0
                }
            }
            
        elif path == '/api/admin/export':
            csv_content = """PyTech Arena Placement Report
Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """

OVERALL STATISTICS
Total Students,3
Placed Students,0
Placement Rate (%),0.0

DEPARTMENT-WISE STATISTICS
Department,Total Students,Average GPA
Computer Science,1,9.0
Electronics and Communication Engineering,1,9.2
Mechanical Engineering,1,8.1

STUDENT DETAILS
Name,Email,Department,GPA,Placement Status
Dr. Ramesh Kumar,placement@jntugv.edu.in,Admin,N/A,Placed
Arun Kumar,arun.kumar@jntugv.edu.in,Computer Science,9.0,Not Placed
Priya Sharma,priya.sharma@jntugv.edu.in,Electronics and Communication Engineering,9.2,Not Placed
Rahul Verma,rahul.verma@jntugv.edu.in,Mechanical Engineering,8.1,Not Placed"""
            
            response_data = {
                'status': 'success',
                'message': 'Export data generated successfully',
                'data': {
                    'csv_content': csv_content,
                    'filename': f'pytech_arena_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    'total_records': 4
                }
            }
            
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
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps(response_data)
            }
        
        # Return successful response
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        # Return error response
        error_data = {
            'status': 'error',
            'message': f'Serverless function error: {str(e)}',
            'timestamp': datetime.utcnow().isoformat(),
            'url': 'https://teamx-seven.vercel.app'
        }
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps(error_data)
        }
