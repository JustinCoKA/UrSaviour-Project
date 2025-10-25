import json
import sys
import os

def lambda_handler(event, context):
    try:
        print(f"Python version: {sys.version}")
        print(f"Python path: {sys.path}")
        
        import fitz
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'message': f'PyMuPDF imported successfully! Version: {fitz.version}',
                'python_version': sys.version,
                'python_path': sys.path[:5]  # 처음 5개만
            })
        }
    except ImportError as e:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'error',
                'message': f'PyMuPDF import failed: {str(e)}',
                'python_version': sys.version,
                'python_path': sys.path[:5]  # 처음 5개만
            })
        }