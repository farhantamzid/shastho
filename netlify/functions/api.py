from flask import Flask, request
import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the Flask app
from app import app

def handler(event, context):
    """Netlify Function handler to proxy requests to Flask app."""
    # Parse the request from the event
    path = event['path']
    http_method = event['httpMethod']
    headers = event['headers'] or {}
    query_string = event['queryStringParameters'] or {}
    body = event['body'] or ''

    # Convert Netlify's request format to WSGI format
    environ = {
        'REQUEST_METHOD': http_method,
        'PATH_INFO': path,
        'QUERY_STRING': '&'.join([f"{k}={v}" for k, v in query_string.items()]) if query_string else '',
        'CONTENT_LENGTH': str(len(body)),
        'wsgi.input': body,
        'HTTP_HOST': headers.get('host', 'localhost'),
    }

    # Add HTTP headers
    for header, value in headers.items():
        key = header.upper().replace('-', '_')
        if key not in ('CONTENT_LENGTH', 'CONTENT_TYPE'):
            key = f'HTTP_{key}'
        environ[key] = value

    # Capture the response from Flask
    response_status = None
    response_headers = []
    response_body = []

    def start_response(status, headers):
        nonlocal response_status, response_headers
        response_status = status
        response_headers = headers

    # Run the Flask app
    response = app(environ, start_response)

    # Combine response body parts
    for chunk in response:
        if chunk:
            response_body.append(chunk.decode('utf-8'))

    # Format response for Netlify
    status_code = int(response_status.split()[0])
    headers_dict = dict(response_headers)

    return {
        'statusCode': status_code,
        'headers': headers_dict,
        'body': ''.join(response_body),
        'isBase64Encoded': False,
    }