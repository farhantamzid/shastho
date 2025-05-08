from flask import request, session
from app import create_app
import socket

app = create_app()

def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

if __name__ == '__main__':
    # Try ports 5000, 5001, 5002 in sequence
    for port in [5000, 5001, 5002, 5003]:
        if not is_port_in_use(port):
            print(f"Starting app on port {port}")
            app.run(debug=True, port=port)
            break
    else:
        print("Could not find an available port from 5000-5003")
        print("Please specify a port manually or free up one of these ports")