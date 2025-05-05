from flask import request, session
from app import create_app

app = create_app()

# Removed unnecessary middleware placeholder

if __name__ == '__main__':
    app.run(debug=True)