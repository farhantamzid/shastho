from flask import request, session
from app import create_app
from app.utils.audit import log_login, log_logout

app = create_app()

# Setup audit logging middleware
@app.before_request
def audit_request_middleware():
    pass  # Placeholder for any pre-request audit logging if needed

if __name__ == '__main__':
    app.run(debug=True)